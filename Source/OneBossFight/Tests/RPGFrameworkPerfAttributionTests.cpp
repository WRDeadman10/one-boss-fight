#if WITH_DEV_AUTOMATION_TESTS
#include <limits>
#include "Misc/AutomationTest.h"
#include "Boss/RPGFrameworkPerfAttribution.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFrameworkPerfCounterMath,
	"OneBossFight.Framework.PerfAttribution.CounterMath",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGFrameworkPerfCounterMath::RunTest(const FString&)
{
	RPGFrameworkPerfAttribution::FWindow Window;
	Window.RecordMilliseconds(1.25);
	Window.RecordMilliseconds(0.0004);
	TestEqual(TEXT("valid samples accumulate"), Window.Samples, uint64(2));
	TestEqual(TEXT("durations are rounded to microseconds"), Window.TotalMicroseconds, uint64(1250));
	TestEqual(TEXT("maximum sample is retained"), Window.MaxMicroseconds, uint64(1250));

	Window.RecordMilliseconds(-1.0);
	Window.RecordMilliseconds(std::numeric_limits<double>::quiet_NaN());
	TestEqual(TEXT("negative and non-finite samples are ignored"), Window.Samples, uint64(2));

	Window.TotalMicroseconds = MAX_uint64 - 10;
	Window.RecordMilliseconds(1.0);
	TestEqual(TEXT("total duration saturates instead of overflowing"), Window.TotalMicroseconds, MAX_uint64);
	Window.Samples = MAX_uint64;
	Window.RecordMilliseconds(0.0);
	TestEqual(TEXT("sample count saturates instead of overflowing"), Window.Samples, MAX_uint64);

	Window.Reset();
	TestEqual(TEXT("reset clears samples"), Window.Samples, uint64(0));
	TestEqual(TEXT("reset clears total"), Window.TotalMicroseconds, uint64(0));
	TestEqual(TEXT("reset clears maximum"), Window.MaxMicroseconds, uint64(0));
	return true;
}
#endif
