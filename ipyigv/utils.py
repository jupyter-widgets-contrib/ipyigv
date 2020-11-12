from ipywidgets import Widget, widget_serialization


def _widget_to_json_no_none(x, obj):
    if isinstance(x, dict):
        return {k: _widget_to_json_no_none(v, obj) for k, v in x.items() if v is not None}
    elif isinstance(x, (list, tuple)):
        return [_widget_to_json_no_none(v, obj) for v in x if v is not None]
    elif isinstance(x, Widget):
        return "IPY_MODEL_" + x.model_id
    else:
        return x

widget_serialization_no_none = {
    'to_json': _widget_to_json_no_none,
    'from_json': widget_serialization['from_json']
}


# from Django project:
# https://github.com/django/django/blob/master/django/core/validators.py

# class RegexValidator:
#     regex = ''
#     message = _('Enter a valid value.')
#     code = 'invalid'
#     inverse_match = False
#     flags = 0
#
#     def __init__(self, regex=None, message=None, code=None, inverse_match=None, flags=None):
#         if regex is not None:
#             self.regex = regex
#         if message is not None:
#             self.message = message
#         if code is not None:
#             self.code = code
#         if inverse_match is not None:
#             self.inverse_match = inverse_match
#         if flags is not None:
#             self.flags = flags
#         if self.flags and not isinstance(self.regex, str):
#             raise TypeError("If the flags are set, regex must be a regular expression string.")
#
#         self.regex = _lazy_re_compile(self.regex, self.flags)
#
#     def __call__(self, value):
#         """
#         Validate that the input contains (or does *not* contain, if
#         inverse_match is True) a match for the regular expression.
#         """
#         regex_matches = self.regex.search(str(value))
#         invalid_input = regex_matches if self.inverse_match else not regex_matches
#         if invalid_input:
#             raise ValidationError(self.message, code=self.code, params={'value': value})
#
#     def __eq__(self, other):
#         return (
#             isinstance(other, RegexValidator) and
#             self.regex.pattern == other.regex.pattern and
#             self.regex.flags == other.regex.flags and
#             (self.message == other.message) and
#             (self.code == other.code) and
#             (self.inverse_match == other.inverse_match)
#         )
#
#
# class URLValidator(RegexValidator):
#     ul = '\u00a1-\uffff'  # Unicode letters range (must not be a raw string).
#
#     # IP patterns
#     ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
#     ipv6_re = r'\[[0-9a-f:.]+\]'  # (simple regex, validated later)
#
#     # Host patterns
#     hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
#     # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
#     domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
#     tld_re = (
#         r'\.'                                # dot
#         r'(?!-)'                             # can't start with a dash
#         r'(?:[a-z' + ul + '-]{2,63}'         # domain label
#         r'|xn--[a-z0-9]{1,59})'              # or punycode label
#         r'(?<!-)'                            # can't end with a dash
#         r'\.?'                               # may have a trailing dot
#     )
#     host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'
#
#     regex = _lazy_re_compile(
#         r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
#         r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
#         r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
#         r'(?::\d{2,5})?'  # port
#         r'(?:[/?#][^\s]*)?'  # resource path
#         r'\Z', re.IGNORECASE)
#     message = _('Enter a valid URL.')
#     schemes = ['http', 'https', 'ftp', 'ftps']
#
#     def __init__(self, schemes=None, **kwargs):
#         super().__init__(**kwargs)
#         if schemes is not None:
#             self.schemes = schemes
#
#     def __call__(self, value):
#         if not isinstance(value, str):
#             raise ValidationError(self.message, code=self.code, params={'value': value})
#         # Check if the scheme is valid.
#         scheme = value.split('://')[0].lower()
#         if scheme not in self.schemes:
#             raise ValidationError(self.message, code=self.code, params={'value': value})
#
#         # Then check full URL
#         try:
#             super().__call__(value)
#         except ValidationError as e:
#             # Trivial case failed. Try for possible IDN domain
#             if value:
#                 try:
#                     scheme, netloc, path, query, fragment = urlsplit(value)
#                 except ValueError:  # for example, "Invalid IPv6 URL"
#                     raise ValidationError(self.message, code=self.code, params={'value': value})
#                 try:
#                     netloc = punycode(netloc)  # IDN -> ACE
#                 except UnicodeError:  # invalid domain part
#                     raise e
#                 url = urlunsplit((scheme, netloc, path, query, fragment))
#                 super().__call__(url)
#             else:
#                 raise
#         else:
#             # Now verify IPv6 in the netloc part
#             host_match = re.search(r'^\[(.+)\](?::\d{2,5})?$', urlsplit(value).netloc)
#             if host_match:
#                 potential_ip = host_match[1]
#                 try:
#                     validate_ipv6_address(potential_ip)
#                 except ValidationError:
#                     raise ValidationError(self.message, code=self.code, params={'value': value})
#
#         # The maximum length of a full host name is 253 characters per RFC 1034
#         # section 3.1. It's defined to be 255 bytes or less, but this includes
#         # one byte for the length of the name and one byte for the trailing dot
#         # that's used to indicate absolute names in DNS.
#         if len(urlsplit(value).netloc) > 253:
#             raise ValidationError(self.message, code=self.code, params={'value': value})
#
