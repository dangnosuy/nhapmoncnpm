"""
Unit tests cho backend/common/savings_rules.py

Coverage:
  - days_between: tính số ngày giữa 2 thời điểm
  - term_days: chuyển kỳ hạn (tháng) sang ngày
  - rule_days_to_real_days: chuyển đổi ngày quy tắc
  - years_from_days: chuyển ngày sang năm (365 ngày = 1 năm)
  - calculate_interest: tính lãi suất
  - get_applicable_interest_rate: xác định lãi suất áp dụng (QĐ3)
  - demo_maturity_date: tính ngày đáo hạn
  - demo_elapsed_display: hiển thị thời gian đã gửi
  - is_matured: kiểm tra đáo hạn
  - check_auto_rollover: tự động tái tục
  - get_config / get_float_config / get_int_config: đọc config từ DB
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call
from dateutil.relativedelta import relativedelta

# Add backend directory to path so we can import savings_rules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.savings_rules import (
    days_between,
    term_days,
    rule_days_to_real_days,
    years_from_days,
    calculate_interest,
    get_applicable_interest_rate,
    demo_maturity_date,
    demo_elapsed_display,
    is_matured,
    check_auto_rollover,
    get_config,
    get_float_config,
    get_int_config,
    get_non_term_rate,
    DAYS_PER_YEAR,
)


# ============================================================================
# days_between
# ============================================================================

class TestDaysBetween:
    """Test hàm days_between — tính số ngày giữa 2 thời điểm."""

    def test_same_day_returns_zero(self):
        now = datetime(2026, 5, 31, 12, 0, 0)
        assert days_between(now, now) == 0

    def test_one_day_elapsed(self):
        start = datetime(2026, 5, 30, 12, 0, 0)
        end = datetime(2026, 5, 31, 12, 0, 0)
        assert days_between(start, end) == pytest.approx(1.0, abs=0.01)

    def test_30_days_elapsed(self):
        start = datetime(2026, 5, 1, 0, 0, 0)
        end = datetime(2026, 5, 31, 0, 0, 0)
        assert days_between(start, end) == pytest.approx(30.0, abs=0.01)

    def test_string_input_is_parsed(self):
        start = "2026-05-01T00:00:00"
        end = datetime(2026, 5, 31, 0, 0, 0)
        assert days_between(start, end) == pytest.approx(30.0, abs=0.01)

    def test_ended_at_defaults_to_now(self):
        start = datetime.now() - timedelta(days=5)
        result = days_between(start)
        assert result == pytest.approx(5.0, abs=0.1)

    def test_negative_elapsed_returns_zero(self):
        """Nếu ended_at < started_at, trả về 0 (max(..., 0))."""
        start = datetime(2026, 6, 1)
        end = datetime(2026, 5, 31)
        assert days_between(start, end) == 0

    def test_fractional_days(self):
        """12 giờ = 0.5 ngày."""
        start = datetime(2026, 5, 31, 0, 0, 0)
        end = datetime(2026, 5, 31, 12, 0, 0)
        assert days_between(start, end) == pytest.approx(0.5, abs=0.01)

    def test_cross_month_boundary(self):
        start = datetime(2026, 2, 15)
        end = datetime(2026, 3, 15)
        assert days_between(start, end) == pytest.approx(28.0, abs=0.01)

    def test_cross_year_boundary(self):
        start = datetime(2025, 12, 31)
        end = datetime(2026, 1, 1)
        assert days_between(start, end) == pytest.approx(1.0, abs=0.01)


# ============================================================================
# term_days
# ============================================================================

class TestTermDays:
    """Test hàm term_days — 1 tháng = 30 ngày."""

    def test_zero_months(self):
        assert term_days(0) == 0

    def test_none_months(self):
        assert term_days(None) == 0

    def test_1_month(self):
        assert term_days(1) == 30

    def test_3_months(self):
        assert term_days(3) == 90

    def test_6_months(self):
        assert term_days(6) == 180

    def test_12_months(self):
        assert term_days(12) == 360

    def test_returns_int(self):
        assert isinstance(term_days(3), int)


# ============================================================================
# rule_days_to_real_days
# ============================================================================

class TestRuleDaysToRealDays:
    """Test hàm rule_days_to_real_days."""

    def test_positive_days(self):
        assert rule_days_to_real_days(15) == 15.0

    def test_zero_days(self):
        assert rule_days_to_real_days(0) == 0.0

    def test_none_returns_zero(self):
        assert rule_days_to_real_days(None) == 0.0

    def test_negative_returns_zero(self):
        """max(..., 0) bảo vệ khỏi giá trị âm."""
        assert rule_days_to_real_days(-5) == 0.0

    def test_returns_float(self):
        assert isinstance(rule_days_to_real_days(15), float)


# ============================================================================
# years_from_days
# ============================================================================

class TestYearsFromDays:
    """Test hàm years_from_days — 365 ngày = 1 năm."""

    def test_365_days_is_one_year(self):
        assert years_from_days(365) == pytest.approx(1.0)

    def test_zero_days(self):
        assert years_from_days(0) == 0.0

    def test_none_returns_zero(self):
        assert years_from_days(None) == 0.0

    def test_180_days(self):
        assert years_from_days(180) == pytest.approx(180 / 365)

    def test_90_days(self):
        assert years_from_days(90) == pytest.approx(90 / 365)

    def test_negative_returns_zero(self):
        assert years_from_days(-10) == 0.0

    def test_1_day(self):
        assert years_from_days(1) == pytest.approx(1 / 365)

    def test_730_days_is_2_years(self):
        assert years_from_days(730) == pytest.approx(2.0)


# ============================================================================
# calculate_interest
# ============================================================================

class TestCalculateInterest:
    """Test hàm calculate_interest — công thức: principal × rate / 100 × (days / 365)."""

    def test_basic_interest(self):
        """10 triệu, 5%/năm, 365 ngày → lãi = 500,000."""
        result = calculate_interest(10_000_000, 5.0, 365)
        assert result == 500_000.0

    def test_3_month_term_interest(self):
        """10 triệu, 5%/năm, 90 ngày → lãi ≈ 123,287.67."""
        result = calculate_interest(10_000_000, 5.0, 90)
        expected = round(10_000_000 * 5.0 / 100 * (90 / 365), 2)
        assert result == pytest.approx(expected, abs=0.01)

    def test_non_term_interest_15_days(self):
        """10 triệu, 0.5%/năm, 15 ngày."""
        result = calculate_interest(10_000_000, 0.5, 15)
        expected = round(10_000_000 * 0.5 / 100 * (15 / 365), 2)
        assert result == pytest.approx(expected, abs=0.01)

    def test_zero_principal(self):
        assert calculate_interest(0, 5.0, 90) == 0.0

    def test_none_principal(self):
        assert calculate_interest(None, 5.0, 90) == 0.0

    def test_zero_rate(self):
        assert calculate_interest(10_000_000, 0, 90) == 0.0

    def test_none_rate(self):
        assert calculate_interest(10_000_000, None, 90) == 0.0

    def test_zero_days(self):
        assert calculate_interest(10_000_000, 5.0, 0) == 0.0

    def test_returns_2_decimal_places(self):
        result = calculate_interest(1_000_000, 5.5, 180)
        # Verify it's rounded to 2 decimal places
        assert result == round(result, 2)

    def test_large_amount(self):
        """1 tỷ, 5.5%/năm, 180 ngày."""
        result = calculate_interest(1_000_000_000, 5.5, 180)
        expected = round(1_000_000_000 * 5.5 / 100 * (180 / 365), 2)
        assert result == pytest.approx(expected, abs=0.01)

    def test_6_month_term(self):
        """5 triệu, 5.5%/năm, 180 ngày (6 tháng)."""
        result = calculate_interest(5_000_000, 5.5, 180)
        expected = round(5_000_000 * 5.5 / 100 * (180 / 365), 2)
        assert result == pytest.approx(expected, abs=0.01)


# ============================================================================
# get_non_term_rate
# ============================================================================

class TestGetNonTermRate:
    """Test hàm get_non_term_rate — lấy lãi suất không kỳ hạn từ DB."""

    def test_returns_rate_from_db(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = (0.5,)
        result = get_non_term_rate(cursor)
        assert result == 0.5
        cursor.execute.assert_called_once()

    def test_fallback_when_no_row(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        result = get_non_term_rate(cursor)
        assert result == 0.5  # fallback default

    def test_queries_correct_columns(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = (1.0,)
        get_non_term_rate(cursor)
        call_args = cursor.execute.call_args
        assert "interest_rate" in call_args[0][0]
        assert "savings_products" in call_args[0][0]
        assert "term_months = 0" in call_args[0][0]


# ============================================================================
# get_applicable_interest_rate (QĐ3)
# ============================================================================

class TestGetApplicableInterestRate:
    """Test hàm get_applicable_interest_rate — quy tắc lãi suất QĐ3.

    QĐ3:
    - Sổ có kỳ hạn rút TRƯỚC đáo hạn → lãi suất không kỳ hạn (0.5%)
    - Sổ có kỳ hạn rút ĐÚNG/SAU đáo hạn → lãi suất sản phẩm
    - Sổ không kỳ hạn → luôn dùng lãi suất sản phẩm
    """

    def test_non_term_always_own_rate(self):
        """Sổ không kỳ hạn luôn dùng lãi suất của sản phẩm."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, 0, 0.5, 10)
        assert result == 0.5
        # Không query DB vì không cần get_non_term_rate
        cursor.execute.assert_not_called()

    def test_non_term_always_own_rate_long_held(self):
        """Sổ không kỳ hạn giữ lâu vẫn dùng lãi suất sản phẩm."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, 0, 0.5, 365)
        assert result == 0.5

    def test_term_before_maturity_gets_non_term_rate(self):
        """Sổ 3 tháng (90 ngày), mới giữ 60 ngày → áp dụng lãi suất không kỳ hạn."""
        cursor = MagicMock()
        cursor.fetchone.return_value = (0.5,)  # non-term rate from DB
        result = get_applicable_interest_rate(cursor, 3, 5.0, 60)
        assert result == 0.5

    def test_term_at_maturity_gets_product_rate(self):
        """Sổ 3 tháng (90 ngày), giữ đúng 90 ngày → lãi suất sản phẩm 5%."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, 3, 5.0, 90)
        assert result == 5.0

    def test_term_after_maturity_gets_product_rate(self):
        """Sổ 3 tháng (90 ngày), giữ 120 ngày → lãi suất sản phẩm 5%."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, 3, 5.0, 120)
        assert result == 5.0

    def test_6_month_term_before_maturity(self):
        """Sổ 6 tháng (180 ngày), giữ 100 ngày → non-term rate."""
        cursor = MagicMock()
        cursor.fetchone.return_value = (0.5,)
        result = get_applicable_interest_rate(cursor, 6, 5.5, 100)
        assert result == 0.5

    def test_6_month_term_at_maturity(self):
        """Sổ 6 tháng (180 ngày), giữ đúng 180 ngày → product rate."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, 6, 5.5, 180)
        assert result == 5.5

    def test_none_term_months_treated_as_non_term(self):
        """term_months = None → xem như không kỳ hạn."""
        cursor = MagicMock()
        result = get_applicable_interest_rate(cursor, None, 0.5, 10)
        assert result == 0.5

    def test_1_day_before_maturity(self):
        """Sổ 3 tháng (90 ngày), giữ 89 ngày → vẫn bị phạt."""
        cursor = MagicMock()
        cursor.fetchone.return_value = (0.5,)
        result = get_applicable_interest_rate(cursor, 3, 5.0, 89)
        assert result == 0.5


# ============================================================================
# demo_maturity_date
# ============================================================================

class TestDemoMaturityDate:
    """Test hàm demo_maturity_date — tính ngày đáo hạn hiển thị."""

    def test_3_month_term(self):
        opened = datetime(2026, 1, 15)
        result = demo_maturity_date(opened, 3)
        assert result == "2026-04-15"

    def test_6_month_term(self):
        opened = datetime(2026, 1, 1)
        result = demo_maturity_date(opened, 6)
        assert result == "2026-07-01"

    def test_12_month_term(self):
        opened = datetime(2025, 6, 15)
        result = demo_maturity_date(opened, 12)
        assert result == "2026-06-15"

    def test_non_term_returns_none(self):
        opened = datetime(2026, 1, 1)
        assert demo_maturity_date(opened, 0) is None

    def test_none_term_returns_none(self):
        opened = datetime(2026, 1, 1)
        assert demo_maturity_date(opened, None) is None

    def test_string_opened_at(self):
        result = demo_maturity_date("2026-03-01T10:00:00", 3)
        assert result == "2026-06-01"

    def test_cross_year_maturity(self):
        opened = datetime(2025, 11, 15)
        result = demo_maturity_date(opened, 3)
        assert result == "2026-02-15"

    def test_end_of_month(self):
        opened = datetime(2026, 1, 31)
        result = demo_maturity_date(opened, 1)
        # relativedelta handles end-of-month: Jan 31 + 1 month = Feb 28
        assert result == "2026-02-28"


# ============================================================================
# demo_elapsed_display
# ============================================================================

class TestDemoElapsedDisplay:
    """Test hàm demo_elapsed_display — hiển thị thời gian đã gửi."""

    @patch('common.savings_rules.days_between')
    def test_2_months_15_days(self, mock_days):
        mock_days.return_value = 75.0  # 2*30 + 15
        result = demo_elapsed_display(datetime(2026, 1, 1))
        assert result == "2 tháng 15 ngày"

    @patch('common.savings_rules.days_between')
    def test_0_months_5_days(self, mock_days):
        mock_days.return_value = 5.0
        result = demo_elapsed_display(datetime(2026, 5, 26))
        assert result == "5 ngày"

    @patch('common.savings_rules.days_between')
    def test_1_month_0_days(self, mock_days):
        """Khi remaining_days == 0 và đã có tháng → chỉ hiện tháng, bỏ '0 ngày'."""
        mock_days.return_value = 30.0
        result = demo_elapsed_display(datetime(2026, 5, 1))
        assert result == "1 tháng"

    @patch('common.savings_rules.days_between')
    def test_0_days_shows_0_ngay(self, mock_days):
        mock_days.return_value = 0.0
        result = demo_elapsed_display(datetime(2026, 5, 31))
        assert result == "0 ngày"

    @patch('common.savings_rules.days_between')
    def test_12_months(self, mock_days):
        """360 ngày = 12 tháng chẵn → chỉ hiện '12 tháng'."""
        mock_days.return_value = 360.0
        result = demo_elapsed_display(datetime(2025, 6, 1))
        assert result == "12 tháng"

    def test_string_opened_at(self):
        """Chấp nhận string ISO format."""
        with patch('common.savings_rules.days_between', return_value=45.0):
            result = demo_elapsed_display("2026-04-16T00:00:00")
            assert result == "1 tháng 15 ngày"


# ============================================================================
# is_matured
# ============================================================================

class TestIsMatured:
    """Test hàm is_matured — kiểm tra sổ đã đáo hạn chưa."""

    @patch('common.savings_rules.days_between')
    def test_matured_exactly_at_term(self, mock_days):
        mock_days.return_value = 90.0  # 3 tháng = 90 ngày
        assert is_matured(datetime(2026, 3, 1), 3) is True

    @patch('common.savings_rules.days_between')
    def test_not_yet_matured(self, mock_days):
        mock_days.return_value = 89.0  # Thiếu 1 ngày
        assert is_matured(datetime(2026, 3, 1), 3) is False

    @patch('common.savings_rules.days_between')
    def test_past_maturity(self, mock_days):
        mock_days.return_value = 120.0
        assert is_matured(datetime(2026, 1, 1), 3) is True

    @patch('common.savings_rules.days_between')
    def test_non_term_never_matures(self, mock_days):
        """Sổ không kỳ hạn luôn trả False."""
        mock_days.return_value = 999.0
        assert is_matured(datetime(2020, 1, 1), 0) is False

    @patch('common.savings_rules.days_between')
    def test_none_term_never_matures(self, mock_days):
        mock_days.return_value = 999.0
        assert is_matured(datetime(2020, 1, 1), None) is False

    @patch('common.savings_rules.days_between')
    def test_6_month_term_matured(self, mock_days):
        mock_days.return_value = 180.0
        assert is_matured(datetime(2025, 12, 1), 6) is True

    @patch('common.savings_rules.days_between')
    def test_6_month_term_not_matured(self, mock_days):
        mock_days.return_value = 179.0
        assert is_matured(datetime(2025, 12, 1), 6) is False


# ============================================================================
# get_config / get_float_config / get_int_config
# ============================================================================

class TestGetConfig:
    """Test các hàm đọc config từ DB."""

    def test_get_config_found(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("1000000",)
        result = get_config(cursor, "MIN_OPEN_AMOUNT", "500000")
        assert result == "1000000"

    def test_get_config_not_found_returns_default(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        result = get_config(cursor, "NON_EXISTENT", "default_val")
        assert result == "default_val"

    def test_get_float_config_valid(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("1000000",)
        result = get_float_config(cursor, "MIN_OPEN_AMOUNT", 500000)
        assert result == 1000000.0
        assert isinstance(result, float)

    def test_get_float_config_invalid_returns_default(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("not_a_number",)
        result = get_float_config(cursor, "BAD_KEY", 500000)
        assert result == 500000.0

    def test_get_float_config_none_returns_default(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        result = get_float_config(cursor, "MISSING", 500000)
        assert result == 500000.0

    def test_get_int_config_valid(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("15",)
        result = get_int_config(cursor, "NON_TERM_MIN_DAYS", 10)
        assert result == 15
        assert isinstance(result, int)

    def test_get_int_config_float_string(self):
        """Chuỗi '15.5' → int(15.5) = 15."""
        cursor = MagicMock()
        cursor.fetchone.return_value = ("15.5",)
        result = get_int_config(cursor, "KEY", 10)
        assert result == 15

    def test_get_int_config_invalid_returns_default(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("abc",)
        result = get_int_config(cursor, "BAD_KEY", 10)
        assert result == 10


# ============================================================================
# check_auto_rollover
# ============================================================================

class TestCheckAutoRollover:
    """Test hàm check_auto_rollover — tự động tái tục khi đáo hạn."""

    def _make_cursor(self, row=None):
        cursor = MagicMock()
        cursor.fetchone.return_value = row
        return cursor

    def test_non_term_account_no_rollover(self):
        """Sổ không kỳ hạn (term_months=0) không bao giờ tái tục."""
        # account_id=1, principal=10M, opened_at=..., status=ACTIVE, user_id=5, term_months=0, rate=0.5
        cursor = self._make_cursor(
            row=(1, 10_000_000, datetime(2020, 1, 1), 'ACTIVE', 5, 0, 0.5)
        )
        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 1)
        assert result is False

    def test_closed_account_no_rollover(self):
        """Sổ đã đóng không tái tục."""
        cursor = self._make_cursor(
            row=(1, 10_000_000, datetime(2020, 1, 1), 'CLOSED', 5, 3, 5.0)
        )
        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 1)
        assert result is False

    def test_no_account_found(self):
        """Không tìm thấy sổ → trả False."""
        cursor = self._make_cursor(row=None)
        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 999)
        assert result is False

    @patch('common.savings_rules.days_between')
    def test_not_yet_matured_no_rollover(self, mock_days):
        """Chưa đáo hạn → không tái tục."""
        mock_days.return_value = 60.0  # 3 tháng = 90 ngày, mới 60 ngày
        cursor = self._make_cursor(
            row=(1, 10_000_000, datetime(2026, 4, 1), 'ACTIVE', 5, 3, 5.0)
        )
        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 1)
        assert result is False

    @patch('common.savings_rules.days_between')
    def test_matured_3_month_rollover(self, mock_days):
        """Sổ 3 tháng đáo hạn → tái tục 1 lần."""
        mock_days.return_value = 95.0  # > 90 ngày

        cursor = MagicMock()
        # First fetchone: account data
        cursor.fetchone.return_value = (
            1, 10_000_000.0, datetime(2026, 2, 25), 'ACTIVE', 5, 3, 5.0
        )

        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 1)
        assert result is True

        # Verify UPDATE was called
        update_calls = [
            c for c in cursor.execute.call_args_list
            if 'UPDATE' in str(c)
        ]
        assert len(update_calls) >= 1

        # Verify INSERT transaction was called
        insert_calls = [
            c for c in cursor.execute.call_args_list
            if 'INSERT' in str(c) and 'AUTO_ROLLOVER' in str(c)
        ]
        assert len(insert_calls) == 1

        # Verify commit was called
        conn.commit.assert_called_once()

    @patch('common.savings_rules.days_between')
    def test_multiple_terms_elapsed(self, mock_days):
        """Nhiều kỳ hạn trôi qua → tái tục nhiều lần."""
        # Sổ 3 tháng (90 ngày), đã trôi qua 200 ngày (> 2 kỳ)
        mock_days.return_value = 200.0

        cursor = MagicMock()
        cursor.fetchone.return_value = (
            1, 10_000_000.0, datetime(2025, 11, 13), 'ACTIVE', 5, 3, 5.0
        )
        conn = MagicMock()
        result = check_auto_rollover(cursor, conn, 1)
        assert result is True

        # Verify principal was updated (should be > 10M due to compounding)
        update_calls = [c for c in cursor.execute.call_args_list if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1
        # The updated principal should be > original
        updated_principal = update_calls[0][0][1][0]
        assert updated_principal > 10_000_000.0


# ============================================================================
# Edge cases & Integration-style tests
# ============================================================================

class TestEdgeCases:
    """Test các trường hợp biên."""

    def test_interest_calculation_consistency(self):
        """Kiểm tra tính nhất quán: lãi 1 năm = principal × rate / 100."""
        principal = 10_000_000
        rate = 5.0
        interest_365 = calculate_interest(principal, rate, 365)
        expected = principal * rate / 100  # 500,000
        assert interest_365 == pytest.approx(expected, abs=0.01)

    def test_interest_additivity(self):
        """Lãi của N ngày = tổng lãi của từng phần (tuyến tính)."""
        p, r = 10_000_000, 5.0
        interest_90 = calculate_interest(p, r, 90)
        interest_60 = calculate_interest(p, r, 60)
        interest_30 = calculate_interest(p, r, 30)
        assert interest_90 == pytest.approx(interest_60 + interest_30, abs=0.02)

    def test_min_open_amount_boundary(self):
        """Số tiền đúng bằng MIN_OPEN_AMOUNT (1M) → tính lãi được."""
        result = calculate_interest(1_000_000, 5.0, 90)
        assert result > 0

    def test_qd3_penalty_significant(self):
        """Phạt lãi suất QĐ3: chênh lệch giữa đúng hạn và trước hạn phải đáng kể."""
        principal = 100_000_000
        days = 89  # Trước hạn 1 ngày (kỳ hạn 90 ngày)

        # Lãi đúng hạn (5%/năm)
        correct_rate_interest = calculate_interest(principal, 5.0, days)

        # Lãi phạt (0.5%/năm)
        penalty_interest = calculate_interest(principal, 0.5, days)

        # Chênh lệch phải đáng kể (~10 lần)
        assert correct_rate_interest > penalty_interest * 5

    def test_days_between_dst_safe(self):
        """days_between dùng total_seconds / 86400, không phụ thuộc DST."""
        # Tạo 2 thời điểm cách nhau đúng 1 ngày
        start = datetime(2026, 3, 8, 12, 0, 0)  # DST change in US
        end = datetime(2026, 3, 9, 12, 0, 0)
        result = days_between(start, end)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_term_days_consistency(self):
        """term_days phải nhất quán: N tháng = N × 30 ngày."""
        for months in range(0, 25):
            assert term_days(months) == months * 30
