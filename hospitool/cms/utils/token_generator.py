# Copyright [2019] [Integreat Project]
# Copyright [2023] [YCMS]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This module contains helpers for the account activation process
(also see :class:`~hospitool.cms.views.authentication.account_activation_view.AccountActivationView`).
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """
    This token generator is identical to the default password reset token generator of :mod:`django.contrib.auth` with
    the exception of the used HMAC salt.
    This means password reset tokens are no longer accepted for the account activation and vice versa.
    """

    key_salt = "hospitool.cms.utils.token_generator.PasswordResetTokenGenerator"


password_reset_token_generator = CustomPasswordResetTokenGenerator()
