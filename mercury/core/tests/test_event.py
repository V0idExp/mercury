from unittest.mock import Mock

from ..event import Event


def test_event_sub_unsub(mocker: Mock):
    listener = mocker.Mock()

    # subscribe to an event and check the call
    ev = Event('some_event')
    ev += listener
    ev('some_arg')

    listener.assert_called_once_with(('some_arg'))
    listener.reset_mock()

    # try to double-subscribe, there should still be one call
    ev += listener
    ev('another_call_arg')
    listener.assert_called_once_with(('another_call_arg'))
    listener.reset_mock()

    # remove the subscription, there should be no calls afterwards
    ev -= listener
    ev('yet_another_call')
    listener.assert_not_called()
