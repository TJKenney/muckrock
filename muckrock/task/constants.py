"""Constants for the Task Application"""

SNAIL_MAIL_CATEGORIES = [
    ('a', 'Appeal'),
    ('n', 'New'),
    ('u', 'Update'),
    ('f', 'Followup'),
    ('p', 'Payment'),
]
PORTAL_CATEGORIES = [('i', 'Incoming')] + SNAIL_MAIL_CATEGORIES
PUBLIC_FLAG_CATEGORIES = [
    (
        'move communication',
        'A communication ended up on this request inappropriately.',
    ),
    (
        'no response',
        'This agency hasn\'t responded after multiple submissions.',
    ),
    (
        'wrong agency',
        'The agency has indicated that this request should be directed to '
        'another agency.',
    ),
    (
        'missing documents',
        'I should have received documents for this request.',
    ),
    (
        'form',
        'The agency has asked that you use a form.',
    ),
    (
        'follow-up complaints',
        'Agency is complaining about follow-up messages.',
    ),
    (
        'appeal',
        'Should I appeal this response?',
    ),
    (
        'proxy',
        'The agency denied the request due to an in-state citzenship law.',
    ),
]
PRIVATE_FLAG_CATEGORIES = [
    (
        'contact info changed',
        'User supplied contact info.',
    ),
    (
        'no proxy',
        'No proxy was available.',
    ),
    (
        'agency update',
        'An agency logged in to the site and updated a request.',
    ),
    (
        'agency new email',
        'An agency with no primary email set replied via email.',
    ),
]
FLAG_CATEGORIES = PUBLIC_FLAG_CATEGORIES + PRIVATE_FLAG_CATEGORIES
