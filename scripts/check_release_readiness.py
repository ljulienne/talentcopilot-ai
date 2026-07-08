from talentcopilot.services.release_readiness_service import ReleaseReadinessService


def main():
    report = ReleaseReadinessService().build()
    print(f"Release readiness: {report.score}% - {report.status}")
    for check in report.checks:
        print(f"[{check.status}] {check.name}: {check.detail}")
    if report.score < 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
