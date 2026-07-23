def validate_statutory_leave(leave_type: str, days_requested: int, available_balance: int, has_med_cert: bool):
    """
    Validates leave requests according to the Employment Act of Kenya.
    """
    # Sec 28: Annual Leave check
    if leave_type == 'annual' and days_requested > available_balance:
        raise ValueError(f"Insufficient leave balance. You have {available_balance} days available.")
    
    # Sec 29: Maternity Leave check (90 days max)
    if leave_type == 'maternity' and days_requested > 90:
        raise ValueError("Statutory limit error: Maternity leave cannot exceed 90 calendar days.")
        
    # Sec 29: Paternity Leave check (14 days max)
    if leave_type == 'paternity' and days_requested > 14:
        raise ValueError("Statutory limit error: Paternity leave cannot exceed 14 calendar days.")

    # Sec 30: Sick Leave check (Medical cert mandatory if > 1 day)
    if leave_type == 'sick' and days_requested > 1 and not has_med_cert:
        raise ValueError("Statutory compliance error: Medical Certificate is mandatory for sick leave exceeding 1 day.")

    return True