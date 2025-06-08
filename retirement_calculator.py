import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

# 그래프 글꼴 설정 (Streamlit Cloud 호환)
font_path = "fonts/NanumGothicCoding.ttf"  # GitHub에 업로드한 폰트 경로
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()

# 페이지 제목
st.set_page_config(page_title="노후 자금 계산기", layout="centered")
st.title("💰 노후 자금 계산기")
st.write("경제 조건을 고려하여 당신의 노후 자금이 충분한지 확인해보세요.")

# 기본 정보
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("현재 나이", min_value=0, max_value=100, value=30)
    gender = st.selectbox("성별", ["남성", "여성"])
with col2:
    retirement_age = st.number_input("희망 은퇴 나이", min_value=40, max_value=100, value=60)
    expect_long_life = st.checkbox("100세 이상 대비")

# 예상 수명 설정
life_expectancy = 100 if expect_long_life else (83 if gender == "남성" else 86)

# 수입 및 자산
st.subheader("📊 경제 조건 입력")
monthly_income = st.number_input("연금 외 월수입 (만원)", min_value=0, value=50)
pension = st.number_input("예상 월 연금 수령액 (만원)", min_value=0, value=100)
debt = st.number_input("현재 총 부채 (만원)", min_value=0, value=0)
assets = st.number_input("보유 자산 (만원)", min_value=0, value=10000)
avg_inflation_rate = 0.025  #평균 인플레이션율 2.5% 자동 적용
st.caption("💡 기준 인플레이션율 2.5%가 자동 적용되어 연간 지출이 계산됩니다.")

# 사용자의 연간 총수입 계산
annual_total_income = (monthly_income + pension) * 12

# 소득 분위 판별
if annual_total_income < 1500:
    income_bracket = "1분위"
elif annual_total_income >= 3000:
    income_bracket = "5분위"
else:
    income_bracket = "3분위"

# 결과 표시
st.markdown(f"### 💬 추정 소득 분위: {income_bracket}")
st.caption("ℹ️ 소득 분위 기준: 1분위(1,500만 원 미만), 3분위(1,500만~3,000만 원), 5분위(3,000만 원 이상)")

# 월 지출 항목
st.subheader("💸 월 지출 항목 (단위: 만원)")
housing = st.number_input("주거비", min_value=0, value=30)
food = st.number_input("식비", min_value=0, value=20)
health = st.number_input("의료비", min_value=0, value=10)
leisure = st.number_input("여가/기타", min_value=0, value=10)
monthly_expense = housing + food + health + leisure
net_assets = assets - debt

# 부채 이자 및 상환 반영
interest_rate = st.number_input("대출 이자율 (%)", min_value=0.0, value=4.0) / 100
repayment_years = st.number_input("상환 기간 (년)", min_value=1, value=10)
annual_debt_payment = debt * (1 + interest_rate * repayment_years) / repayment_years
monthly_expense += annual_debt_payment / 12  # 월 지출에 부채 상환액 반영

# 계산
years_needed = life_expectancy - retirement_age
monthly_total_income = monthly_income + pension
monthly_shortfall = max(0, monthly_expense - monthly_total_income)
required_funds = monthly_shortfall * 12 * years_needed
remaining_deficit = required_funds - net_assets

# 시각화
years = list(range(1, years_needed + 1))
expenses_by_year = [monthly_expense * 12 * ((1 + avg_inflation_rate) ** i) for i in years]
pensions_by_year = [(pension + monthly_income) * 12 for _ in years]
deficits = [e - p for e, p in zip(expenses_by_year, pensions_by_year)]

fig, ax = plt.subplots()
ax.plot(years, expenses_by_year, label="연간 지출", color='steelblue')
ax.plot(years, pensions_by_year, label="연간 총수입", color='darkorange')
ax.fill_between(years, expenses_by_year, pensions_by_year, where=(np.array(expenses_by_year) > np.array(pensions_by_year)),
                color='lightcoral', alpha=0.4, label="연간 적자")
ax.set_xlabel("은퇴 후 경과 연도")
ax.set_ylabel("금액 (만원)")
ax.set_title("연도별 지출 대비 총수입")
ax.legend()
st.pyplot(fig)

# 요약 멘트
deficit_years = sum(1 for d in deficits if d > 0) # 적자 발생 연도 계산
st.markdown("___")
st.subheader("📝 한줄 요약")

if remaining_deficit <= 0 and deficit_years == 0:
    st.markdown("✅ 현재 자산으로도 노후 준비가 충분합니다.")
elif remaining_deficit > 0 and deficit_years == 0:
    st.markdown(f"🟡 연간 수입은 지출을 커버하지만, 자산이 부족합니다. 예상 부족 금액은 약 {int(remaining_deficit)}만원입니다.")
elif remaining_deficit <= 0 and deficit_years > 0:
    st.markdown(f"🟡 자산은 충분하지만, {deficit_years}년 동안 일시적 적자가 발생할 수 있습니다.")
else:
    st.markdown(f"⚠️ 현재 자산만으로는 부족합니다. 총 {deficit_years}년 동안 적자가 발생할 수 있습니다.")
