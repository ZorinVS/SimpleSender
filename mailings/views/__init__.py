from mailings.views.clients import (
    ClientCreateView,
    ClientListView,
    ClientDetailView,
    ClientUpdateView,
    ClientDeleteView,
)
from mailings.views.messages import (
    MessageCreateView,
    MessageListView,
    MessageDetailView,
    MessageUpdateView,
    MessageDeleteView,
)
from mailings.views.mailings import (
    MailingCreateView,
    MailingListView,
    MailingDetailView,
    MailingUpdateView,
    MailingDeleteView,
    MailingSendView,
    MailingScheduleView,
    MailingCancelView,
    MailingDisableView,
)
from mailings.views.statistics import (
    IndexView,
    MailingAttemptsView,
    UserAttemptsView,
)

__all__ = [
    ClientCreateView,
    ClientListView,
    ClientDetailView,
    ClientUpdateView,
    ClientDeleteView,
    MessageCreateView,
    MessageListView,
    MessageDetailView,
    MessageUpdateView,
    MessageDeleteView,
    MailingCreateView,
    MailingListView,
    MailingDetailView,
    MailingUpdateView,
    MailingDeleteView,
    MailingSendView,
    MailingScheduleView,
    MailingCancelView,
    MailingDisableView,
    IndexView,
    MailingAttemptsView,
    UserAttemptsView,
]
