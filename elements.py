from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
from ableton.v2.base import depends
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v2.control_surface.elements import ButtonMatrixElement, ColorSysexElement, SliderElement, SysexElement
from novation import sysex
from novation.launchpad_elements import (
    BUTTON_FADER_MAIN_CHANNEL,
    BUTTON_FADER_COLOR_CHANNEL,
    SESSION_WIDTH,
    LaunchpadElements,
    create_button,
    create_slider,
)
from . import sysex_ids as ids


class Elements(LaunchpadElements):
    model_id = ids.LP_MINI_X_ID
    default_layout = sysex.KEYS_LAYOUT_BYTE
    button_fader_cc_offset = 21

    @depends(skin=None)
    def __init__(self, skin=None, *a, **k):
        (super(Elements, self).__init__)(*a, **k)
        self.drums_mode_button = create_button(96, "Drums_Mode_Button")
        self.keys_mode_button = create_button(97, "Keys_Mode_Button")
        self.user_mode_button = create_button(98, "User_Mode_Button")
        self.button_faders = ButtonMatrixElement(
            rows=[
                [
                    self._create_slider(index + self.button_fader_cc_offset, "Button_Fader_{}".format(index))
                    for index in range(SESSION_WIDTH)
                ]
            ],
            name="Button_Faders",
        )
        self.button_fader_color_elements_raw = [
            create_button(
                (index + self.button_fader_cc_offset),
                ("Button_Fader_Color_Element_{}".format(index)),
                channel=BUTTON_FADER_MAIN_CHANNEL,
            )
            for index in range(SESSION_WIDTH)
        ]
        self.button_fader_color_elements = ButtonMatrixElement(
            rows=[self.button_fader_color_elements_raw], name="Button_Fader_Color_Elements"
        )

        session_button_color_identifier = sysex.STD_MSG_HEADER + (ids.LP_MINI_X_ID, 20)
        self.session_button_color_element = ColorSysexElement(
            name="Session_Button_Color_Element",
            sysex_identifier=session_button_color_identifier,
            send_message_generator=(lambda v: session_button_color_identifier + v + (sysex.SYSEX_END_BYTE,)),
            skin=skin,
        )
        self.button_fader_setup_element = SysexElement(
            name="Button_Fader_Setup_Element", send_message_generator=(partial(self._fader_setup_message_generator, 0))
        )


    def _create_slider(self, identifier, name, **k):
        slider = DualSliderElement(MIDI_CC_TYPE, BUTTON_FADER_COLOR_CHANNEL, BUTTON_FADER_MAIN_CHANNEL, identifier, name=name, **k)
        slider.set_needs_takeover(False)
        return slider
    
class DualSliderElement(SliderElement):
    def __init__(self, msg_type, channel_send, channel_receive, identifier, *a, **k):
        (super(DualSliderElement, self).__init__)(msg_type, channel_receive, identifier, *a, **k)
        self._original_channel = channel_send
