import unittest

from verify_framework_perf_receipt import validate


def valid_receipt(device_class="target_rtx_2060_super"):
    return {
        "receipt_version": 1,
        "run_id": "run-1",
        "build_id": "build-1",
        "engine_version": "5.5.4",
        "map": "L_SevarogArena",
        "device_class": device_class,
        "sample_window": {"start_seconds": 10.0, "end_seconds": 15.1},
        "cpu_scopes": [{"category": "executor_tick_cpu", "unit": "ms", "samples": 300, "total": 6.2, "maximum": 0.08}],
        "gpu_frame_global_ms": 11.3,
        "gpu_component_attributed": False,
    }


class FrameworkPerfReceiptTests(unittest.TestCase):
    def test_target_gpu_frame_is_not_claimed_as_component_gpu(self):
        self.assertEqual(validate(valid_receipt()), [])

    def test_proxy_class_remains_distinct_from_target(self):
        self.assertEqual(validate(valid_receipt("proxy")), [])

    def test_component_gpu_claim_is_rejected(self):
        data = valid_receipt()
        data["gpu_component_attributed"] = True
        data["gpu_component_ms"] = 4.1
        issues = validate(data)
        self.assertTrue(any("cannot be represented as component-attributed" in issue for issue in issues))
        self.assertTrue(any("gpu_component_ms is forbidden" in issue for issue in issues))

    def test_invalid_window_and_mixed_scope_math_are_rejected(self):
        data = valid_receipt()
        data["sample_window"] = {"start_seconds": 5, "end_seconds": 5}
        data["cpu_scopes"][0]["maximum"] = 9.0
        issues = validate(data)
        self.assertTrue(any("sample_window end" in issue for issue in issues))
        self.assertTrue(any("maximum cannot exceed total" in issue for issue in issues))

    def test_zero_sample_window_can_report_empty_scope(self):
        data = valid_receipt()
        data["cpu_scopes"] = [{"category": "executor_tick_cpu", "unit": "ms", "samples": 0, "total": 0, "maximum": 0}]
        self.assertEqual(validate(data), [])

    def test_boolean_nan_and_unknown_fields_fail_closed(self):
        data = valid_receipt()
        data["cpu_scopes"][0]["samples"] = True
        data["unreviewed_estimate_ms"] = 2.0
        issues = validate(data)
        self.assertTrue(any("samples must be a non-negative integer" in issue for issue in issues))
        self.assertTrue(any("unknown property unreviewed_estimate_ms" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
