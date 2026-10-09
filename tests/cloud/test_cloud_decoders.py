"""Cloud-gated tests for token-authenticated features."""
import os

import pytest

from deltakit import Client


pytestmark = pytest.mark.cloud


requires_token = pytest.mark.skipif(
    not os.environ.get("DELTAKIT_TOKEN"),
    reason="DELTAKIT_TOKEN not set; skipping cloud-dependent test",
)


@requires_token
class TestClientAuthentication:

    def test_client_singleton_exists(self):
        client = Client.get_instance()
        assert client is not None

    def test_set_token_accepts_valid_token(self):
        client = Client.get_instance()
        token = os.environ["DELTAKIT_TOKEN"]
        client.set_token(token)


@requires_token
class TestCloudFeatures:

    @pytest.mark.skip(reason="Awaiting decoder API inspection")
    def test_ambiguity_clustering_decoder_roundtrip(self):
        pass
