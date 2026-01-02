from datetime import timedelta
from app.models.user_model import UserRole

# Configuración simplificada de política (UC-09, RB-03)
POLICIES = {
    UserRole.STUDENT: {
        "loan_days": 15,
        "max_renewals": 2,
        "max_loans": 5,
        "reference_loan_days": 0,  # no referencia
    },
    UserRole.STAFF: {
        "loan_days": 30,
        "max_renewals": 3,
        "max_loans": 10,
        "reference_loan_days": 0,
    },
    UserRole.FACULTY: {
        "loan_days": 60,
        "max_renewals": 4,
        "max_loans": 15,
        "reference_loan_days": 7,  # puede llevar referencia con plazo especial (RB-05, UC-10)
    },
    UserRole.LIBRARIAN: {  
        "loan_days": 60,
        "max_renewals": 10,
        "max_loans": 50,
        "reference_loan_days": 30,
    },
}


def get_policy_for_role(role: UserRole) -> dict:
    return POLICIES[role]


def get_loan_delta_days(role: UserRole, is_reference: bool) -> timedelta:
    policy = get_policy_for_role(role)
    if is_reference:
        days = policy.get("reference_loan_days", 0)
    else:
        days = policy["loan_days"]
    return timedelta(days=days)
