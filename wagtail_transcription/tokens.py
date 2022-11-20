from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.contrib.auth import get_user_model
from typing import Type


class ValidatedVideoDataTokenGenerator(PasswordResetTokenGenerator):
    """
    This token generator allow to create token that can
    be helpfull while determining if video data is valid or not
    """

    def make_token(
        self,
        user: Type[get_user_model()],
        video_id: str,
    ) -> str:
        """
        Return a token that can be used to check if video
        data was validated or not
        """
        return self._make_token_with_timestamp(
            user, video_id, self._num_seconds(self._now())
        )

    def check_token(
        self,
        user: Type[get_user_model()],
        video_id: str,
        token: str,
    ) -> bool:
        """
        Check if user, video_id and token are specified
        """
        if not (user and video_id and token):
            return False

        # Parse the token
        try:
            ts_b36, _ = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Validate token
        if not constant_time_compare(
            self._make_token_with_timestamp(user, video_id, ts), token
        ):
            return False

        return True

    def _make_token_with_timestamp(
        self,
        user: Type[get_user_model()],
        video_id: str,
        timestamp: bytes,
    ) -> str:
        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, video_id, timestamp),
            secret=self.secret,
            algorithm=self.algorithm,
        ).hexdigest()[
            ::2
        ]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(
        self,
        user: Type[get_user_model()],
        video_id: str,
        timestamp: bytes,
    ) -> str:
        """
        Generate hash value that will use to determine if video data
        was validated or not
        """
        return (
            six.text_type(user.pk)
            + six.text_type(user.email)
            + six.text_type(video_id)
            + six.text_type(timestamp)
        )


validated_video_data_token = ValidatedVideoDataTokenGenerator()
