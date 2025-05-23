from unittest import mock

import pytest
from anthropic.types import TextBlockParam
from streamlit.testing.v1 import AppTest

from enterprise_computer_use.streamlit import Sender


@pytest.fixture
def streamlit_app():
    return AppTest.from_file("enterprise_computer_use/streamlit.py")


def test_streamlit(streamlit_app: AppTest):
    streamlit_app.run()
    streamlit_app.text_input[1].set_value("sk-ant-0000000000000").run()
    with mock.patch("enterprise_computer_use.loop.sampling_loop") as patch:
        streamlit_app.chat_input[0].set_value("Hello").run()
        assert patch.called
        assert patch.call_args.kwargs["messages"] == [
            {
                "role": Sender.USER,
                "content": [TextBlockParam(text="Hello", type="text")],
            }
        ]
        assert not streamlit_app.exception
