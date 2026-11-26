
def check_run_alerts(load_pct, minutes, run_id, site_id, end_time):
    """Generate overload and low-load alerts for a generator run."""

    alerts = []

    if load_pct > 100:
        alerts.append({
            "timestamp": end_time,
            "site_id": site_id,
            "type": "OVERLOAD",
            "ref_id": run_id,
            "detail": f"Load exceeded 100%: {load_pct}%"
        })
        return alerts

    if 91 <= load_pct <= 100 and minutes > 60:
        alerts.append({
            "timestamp": end_time,
            "site_id": site_id,
            "type": "OVERLOAD_WARNING",
            "ref_id": run_id,
            "detail": f"High load for {minutes} minutes"
        })

    if load_pct < 30 and minutes > 240:
        alerts.append({
            "timestamp": end_time,
            "site_id": site_id,
            "type": "LOW_LOAD",
            "ref_id": run_id,
            "detail": f"Low load for {minutes} minutes"
        })

    return alerts
