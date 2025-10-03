#!/usr/bin/env python3
"""Manual test script to verify node sensor recovery functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock


# Simulate the integration behavior
class TestNodeSensorRecovery:
    """Test that node sensors are re-created after connection recovery."""

    def __init__(self):
        self.hass = MagicMock()
        self.hass.data = {}
        self.config_entry = MagicMock()
        self.config_entry.entry_id = "test_entry"
        self.coordinator = MagicMock()
        self.client = MagicMock()
        self.added_entities = []

    def mock_add_entities(self, entities):
        """Mock add_entities callback that tracks added entities."""
        self.added_entities.extend(entities)
        print(
            f"✅ Added {len(entities)} node sensors: {[e.node_name for e in entities]}"
        )

    async def test_recovery_flow(self):
        """Test the complete recovery flow."""
        from custom_components.kubernetes.const import DOMAIN
        from custom_components.kubernetes.sensor import (
            _async_discover_and_add_new_node_sensors,
        )

        print("🧪 Testing Node Sensor Recovery Flow")
        print("=" * 50)

        # 1. Setup: Store add_entities callback (simulates async_setup_entry)
        print("1️⃣ Initial setup - storing add_entities callback...")
        self.hass.data[DOMAIN] = {
            self.config_entry.entry_id: {"sensor_add_entities": self.mock_add_entities}
        }

        # 2. Connection loss: Simulate nodes being removed (done by cleanup)
        print("2️⃣ Connection lost - entities cleaned up by coordinator...")

        # 3. Connection restored: Coordinator detects nodes again
        print("3️⃣ Connection restored - coordinator detects nodes...")
        self.coordinator.data = {
            "nodes": {
                "manta": {"status": "Ready"},
                "skidbladnir": {"status": "Ready"},
                "william": {"status": "Ready"},
                "yumi": {"status": "Ready"},
            }
        }
        print(f"   Coordinator now has {len(self.coordinator.data['nodes'])} nodes")

        # 4. Simulate entity registry (no existing node sensors after cleanup)
        print("4️⃣ Checking entity registry - no existing node sensors...")
        mock_entity_registry = MagicMock()
        mock_entity_registry.entities.get_entries_for_config_entry_id.return_value = []

        # 5. Trigger discovery (this would normally be called by coordinator listener)
        print("5️⃣ Triggering dynamic node sensor discovery...")

        # Mock the entity registry import
        import sys
        from unittest.mock import patch

        with patch(
            "custom_components.kubernetes.sensor.async_get_entity_registry",
            return_value=mock_entity_registry,
        ):
            await _async_discover_and_add_new_node_sensors(
                self.hass, self.config_entry, self.coordinator, self.client
            )

        # 6. Verify results
        print("6️⃣ Verifying results...")
        print(f"   Expected: 4 node sensors to be created")
        print(f"   Actual: {len(self.added_entities)} node sensors created")

        if len(self.added_entities) == 4:
            node_names = [e.node_name for e in self.added_entities]
            expected_nodes = ["manta", "skidbladnir", "william", "yumi"]
            if set(node_names) == set(expected_nodes):
                print("✅ SUCCESS: All node sensors were re-created correctly!")
                return True
            else:
                print(
                    f"❌ FAIL: Wrong node names. Got {node_names}, expected {expected_nodes}"
                )
                return False
        else:
            print(f"❌ FAIL: Wrong number of sensors created")
            return False


async def main():
    """Run the test."""
    test = TestNodeSensorRecovery()
    success = await test.test_recovery_flow()

    print("\n" + "=" * 50)
    if success:
        print("🎉 NODE SENSOR RECOVERY TEST PASSED!")
        print("The implementation should fix the connection recovery issue.")
    else:
        print("💥 NODE SENSOR RECOVERY TEST FAILED!")
        print("The implementation needs more work.")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
