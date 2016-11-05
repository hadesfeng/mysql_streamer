# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from replication_handler.components.position_finder import PositionFinder
from replication_handler.models.global_event_state import EventType
from replication_handler.models.schema_event_state import SchemaEventState
from replication_handler.models.schema_event_state import SchemaEventStatus
from replication_handler.util.position import GtidPosition


class TestPositionFinder(object):

    @pytest.fixture
    def create_table_statement(self):
        return "CREATE TABLE STATEMENT"

    @pytest.fixture
    def position_dict(self):
        return {"gtid": "sid:12"}

    @pytest.fixture
    def completed_schema_event_state(self, create_table_statement, position_dict):
        return SchemaEventState(
            position=position_dict,
            status=SchemaEventStatus.COMPLETED,
            query=create_table_statement,
            table_name="Business",
            create_table_statement=create_table_statement,
        )

    @pytest.fixture
    def schema_event_position(self):
        return GtidPosition(gtid="sid:12")

    @pytest.yield_fixture
    def patch_get_latest_schema_event_state(self):
        with mock.patch.object(
            SchemaEventState,
            'get_latest_schema_event_state'
        ) as mock_get_latest_schema_event_state:
            yield mock_get_latest_schema_event_state

    def test_get_position_to_resume_tailing(
        self,
        schema_event_position,
        patch_get_latest_schema_event_state,
        completed_schema_event_state,
        position_dict,
        gtid_enabled
    ):
        global_event_state = mock.Mock(
            event_type=EventType.SCHEMA_EVENT,
            position=position_dict,
        )
        position_finder = PositionFinder(
            gtid_enabled=gtid_enabled,
            global_event_state=global_event_state,
        )
        patch_get_latest_schema_event_state.return_value = completed_schema_event_state
        position = position_finder.get_position_to_resume_tailing_from()
        assert position.to_dict() == schema_event_position.to_dict()
