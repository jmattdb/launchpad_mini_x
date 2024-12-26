from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
from ableton.v2.base import listens
from ableton.v2.control_surface import Layer
from ableton.v2.control_surface.components import SessionOverviewComponent
from ableton.v2.control_surface.mode import AddLayerMode, DelayMode, ImmediateBehaviour, ModesComponent, ReenterBehaviour
from novation import sysex
from novation.colors import Rgb
from novation.instrument_control import InstrumentControlMixin
from novation.novation_base import NovationBase
from novation.session_modes import SessionModesComponent
from . import sysex_ids as ids
from .elements import Elements
from .notifying_background import NotifyingBackgroundComponent
from .skin import skin

SESSION_MODES_SWITCH_DELAY = 0.1


class Launchpad_Mini_X(InstrumentControlMixin, NovationBase):
    model_family_code = ids.LP_MINI_X_FAMILY_CODE
    element_class = Elements
    skin = skin

    def __init__(self, *a, **k):
        self._last_layout_byte = sysex.SESSION_LAYOUT_BYTE
        (super(Launchpad_Mini_X, self).__init__)(*a, **k)

    def on_identified(self, midi_bytes):
        self._elements.firmware_mode_switch.send_value(sysex.DAW_MODE_BYTE)
        self._elements.layout_switch.send_value(self._last_layout_byte)
        super(Launchpad_Mini_X, self).on_identified(midi_bytes)

    def can_lock_to_devices(self):
        return False

    def _create_components(self):
        super(Launchpad_Mini_X, self)._create_components()
        self._create_background()
        self._session_layout_mode = partial(self._elements.layout_switch.send_value, sysex.SESSION_LAYOUT_BYTE)
        # self._create_stop_solo_mute_modes()
        self._create_mixer_modes()
        self._create_session_modes()
        self._Launchpad_Mini_X__on_layout_switch_value.subject = self._elements.layout_switch

    def _create_session_layer(self):
        return super(Launchpad_Mini_X, self)._create_session_layer() + Layer(
            scene_launch_buttons="scene_launch_buttons"
        )

    def _create_stop_solo_mute_modes(self):
        self._stop_solo_mute_modes = ModesComponent(
            name="Stop_Solo_Mute_Modes",
            is_enabled=False,
            support_momentary_mode_cycling=False,
            layer=Layer(cycle_mode_button=(self._elements.scene_launch_buttons_raw[7])),
        )
        bottom_row = self._elements.clip_launch_matrix.submatrix[:, 7:8]
        self._stop_solo_mute_modes.add_mode("launch", None, cycle_mode_button_color="Mode.Launch.On")
        self._stop_solo_mute_modes.add_mode(
            "stop",
            (AddLayerMode(self._session, Layer(stop_track_clip_buttons=bottom_row))),
            cycle_mode_button_color="Session.StopClip",
        )
        self._stop_solo_mute_modes.add_mode(
            "solo", (AddLayerMode(self._mixer, Layer(solo_buttons=bottom_row))), cycle_mode_button_color="Mixer.SoloOn"
        )
        self._stop_solo_mute_modes.add_mode(
            "mute", (AddLayerMode(self._mixer, Layer(mute_buttons=bottom_row))), cycle_mode_button_color="Mixer.MuteOff"
        )
        self._stop_solo_mute_modes.selected_mode = "launch"
        self._stop_solo_mute_modes.set_enabled(True)

    def _create_mixer_modes(self):
        self._mixer_modes = ModesComponent(
            name="Mixer_Modes",
            is_enabled=False,
            enable_skinning=True,
            layer=Layer(
                volume_button=(self._elements.scene_launch_buttons_raw[0]),
                pan_button=(self._elements.scene_launch_buttons_raw[1]),
                send_a_button=(self._elements.scene_launch_buttons_raw[2]),
                send_b_button=(self._elements.scene_launch_buttons_raw[3]),
                stop_button=(self._elements.scene_launch_buttons_raw[4]),
                mute_button=(self._elements.scene_launch_buttons_raw[5]),
                solo_button=(self._elements.scene_launch_buttons_raw[6]),
                arm_button=(self._elements.scene_launch_buttons_raw[7]),
            ),
        )
        bottom_row = self._elements.clip_launch_matrix.submatrix[:, 7:8]
        select_none_mode = partial(setattr, self._mixer_modes, "selected_mode", "none")
        self._mixer_modes.add_mode("none", self._session_layout_mode)
        button_fader_layout_mode = partial(self._elements.layout_switch.send_value, sysex.FADERS_LAYOUT_BYTE)

        def add_fader_mode(name, color, is_pan=False):
            control_dict = {("{}_controls".format(name)): "button_faders"}
            if is_pan:
                control_dict["track_color_controls"] = "button_fader_color_elements"
            else:
                control_dict["static_color_controls"] = "button_fader_color_elements"
            self._mixer_modes.add_mode(
                name,
                (
                    partial(
                        self._elements.button_fader_setup_element.send_value,
                        sysex.FADER_HORIZONTAL_ORIENTATION if is_pan else sysex.FADER_VERTICAL_ORIENTATION,
                        sysex.FADER_BIPOLAR if is_pan else sysex.FADER_UNIPOLAR,
                    ),
                    partial(self._mixer.set_static_color_value, color),
                    self._clear_send_cache_of_button_fader_color_elements,
                    AddLayerMode(self._mixer, Layer(**control_dict)),
                    button_fader_layout_mode,
                ),
                behaviour=ReenterBehaviour(on_reenter=select_none_mode),
            )

        add_fader_mode("volume", Rgb.GREEN.midi_value)
        add_fader_mode("pan", 0, True)
        add_fader_mode("send_a", Rgb.VIOLET.midi_value)
        add_fader_mode("send_b", Rgb.DARK_BLUE.midi_value)
        self._mixer_modes.add_mode(
            "stop",
            (self._session_layout_mode, AddLayerMode(self._session, Layer(stop_track_clip_buttons=bottom_row))),
            behaviour=ReenterBehaviour(on_reenter=select_none_mode),
        )
        self._mixer_modes.add_mode(
            "mute",
            (self._session_layout_mode, AddLayerMode(self._mixer, Layer(mute_buttons=bottom_row))),
            behaviour=ReenterBehaviour(on_reenter=select_none_mode),
        )
        self._mixer_modes.add_mode(
            "solo",
            (self._session_layout_mode, AddLayerMode(self._mixer, Layer(solo_buttons=bottom_row))),
            behaviour=ReenterBehaviour(on_reenter=select_none_mode),
        )
        self._mixer_modes.add_mode(
            "arm",
            (self._session_layout_mode, AddLayerMode(self._mixer, Layer(arm_buttons=bottom_row))),
            behaviour=ReenterBehaviour(on_reenter=select_none_mode),
        )
        self._mixer_modes.selected_mode = "none"

    def _clear_send_cache_of_button_fader_color_elements(self):
        for element in self._elements.button_fader_color_elements_raw:
            element.clear_send_cache()

    def _create_session_modes(self):
        self._session_overview = SessionOverviewComponent(
            name="Session_Overview",
            is_enabled=False,
            session_ring=(self._session_ring),
            enable_skinning=True,
            layer=Layer(button_matrix="clip_launch_matrix"),
        )
        self._session_modes = SessionModesComponent(
            name="Session_Modes",
            is_enabled=False,
            layer=Layer(
                cycle_mode_button="session_mode_button", mode_button_color_control="session_button_color_element"
            ),
        )
        self._session_modes.add_mode("launch", None)
        self._session_modes.add_mode("mixer", DelayMode(self._mixer_modes, SESSION_MODES_SWITCH_DELAY))
        self._session_modes.add_mode(
            "overview",
            (
                self._session_overview,
                AddLayerMode(
                    self._session_navigation,
                    Layer(
                        page_up_button="up_button",
                        page_down_button="down_button",
                        page_left_button="left_button",
                        page_right_button="right_button",
                    ),
                ),
                AddLayerMode(self._background, Layer(scene_launch_buttons="scene_launch_buttons")),
            ),
        )
        self._session_modes.selected_mode = "launch"
        self._session_modes.set_enabled(True)
        self._Launchpad_Mini_X__on_session_mode_changed.subject = self._session_modes

    def _create_background(self):
        self._background = NotifyingBackgroundComponent(
            name="Background",
            is_enabled=False,
            add_nop_listeners=True,
            layer=Layer(
                drums_mode_button="drums_mode_button",
                keys_mode_button="keys_mode_button",
                user_mode_button="user_mode_button",
            ),
        )
        self._background.set_enabled(True)
        self._Launchpad_Mini_X__on_background_control_value.subject = self._background

    @listens("selected_mode")
    def __on_session_mode_changed(self, _):
        self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_background_control_value(self, control, value):
        if value:
            if "Mode" in control.name:
                self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_layout_switch_value(self, value):
        self._last_layout_byte = value
