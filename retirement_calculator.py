import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# 한글 폰트 설정
rcParams['font.family'] = 'Malgun Gothic'   # 또는 다른 한글 폰트 이름
rcParams['axes.unicode_minus'] = False 

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("💸 노후 자금 계산기")

# 1. 성별 선택 + 평균 수명 자동 설정
gender = st.selectbox("성별", ["여성", "남성"])
default_life_expectancy = 86 if gender == "여성" else 80  #평균 수명 구분
long_life = st.checkbox("100세까지 대비하기", value=False)
life_expectancy = 100 if long_life else default_life_expectancy

# 2. 기본 정보
current_age = st.number_input("현재 나이", min_value=20, max_value=100, value=30)
retirement_age = st.number_input("은퇴 예정 나이", min_value=current_age+1, max_value=100, value=65)
years_after_retirement = life_expectancy - retirement_age

# 3. 소비 수준
quintile = st.selectbox("소득 분위 선택(소비 수준 결정용)", ["1분위 (연 1천만원 미만)", "3분위 (연 3~5천만원)", "5분위 (연 1억원 이상)"])
quintile_map = {"1분위 (연 1천만원 미만)": "1분위","3분위 (연 3~5천만원)": "3분위","5분위 (연 1억원 이상)": "5분위"}
default_expense = {"1분위": 110, "3분위": 180, "5분위": 230}
base_monthly_expense = default_expense[quintile_map[quintile]]
st.info(f"선택한 분위 기준 제안 원 지출: {base_monthly_expense}만원")

# 4. 항목별 원 지출
food = st.number_input("식비", value=round(base_monthly_expense * 0.3))
housing = st.number_input("주가비", value=round(base_monthly_expense * 0.25))
medical = st.number_input("의료비", value=round(base_monthly_expense * 0.2))
others = st.number_input("여가 및 기타 소비", value=round(base_monthly_expense * 0.25))

# 5. 수입와 예비 자금
income_input_method = st.radio("연금 계산 방식", ["직접 입력", "자동 계산"])

if income_input_method == "직접 입력":
    monthly_pension = st.number_input("월 연금 수령액 (만원)", min_value=0, value=100, step=10)
else:
    annual_income_level = st.slider("연 소득 (만원)", 500, 10000, 3000, step=100)
    monthly_pension = round(annual_income_level * 0.015 / 12, 1)
    st.info(f"예상 월 연금 수령액은 {monthly_pension}만원입니다.")

reserve_fund = st.number_input("예비 자금 (의료·요양비 대비)", value=3000)
inflation = st.number_input("연 인플레이션(%)", value=2.4) / 100

# 6. 계산
annual_expense = (food + housing + medical + others) * 12
annual_income = monthly_pension * 12
total_need = 0

years = list(range(1, years_after_retirement + 1))
annual_expenses = []
annual_incomes = []
balances = []

for i in years:
    adjusted_expense = annual_expense * ((1 + inflation) ** i)
    annual_expenses.append(adjusted_expense)
    annual_incomes.append(annual_income)
    balances.append(annual_income - adjusted_expense)
    total_need += adjusted_expense - annual_income

total_need += reserve_fund * 10000  # 만원 → 원

# 7. 결과 출력
st.subheader("📊 결과 요약")
st.write(f"🟢 은퇴 후 생존 연수: {years_after_retirement}년")
st.write(f"🔵 총 필요 자금: **{int(total_need):,} 원**")

# 8. 시각화 (구분적 기준)
st.subheader("📉 연도별 지출 대비 연금 수입 (시각화)")
fig, ax = plt.subplots()
ax.plot(years, annual_expenses, label="연간 지출")
ax.plot(years, annual_incomes, label="연간 연금 수입")
ax.fill_between(years, annual_expenses, annual_incomes, where=np.array(annual_expenses) > np.array(annual_incomes), color='red', alpha=0.3, label="자금 부족")
ax.set_xlabel("은퇴 후 경과 연수")
ax.set_ylabel("금액 (만원)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# 9. 요약 문장
st.subheader("📾 분석 요약")
if total_need <= 0:
    st.success("✅ 현재 추정에 따르면 은퇴 이후 자금은 충분할 것으로 보입니다.")
elif total_need < 200000000:
    st.warning("🔶 은퇴 자금은 근소하게 충분하지만, 예기치 않은 의료비나 인플레이션에 주의해야 합니다.")
else:
    st.error("⚠️ 은퇴 이후 예상 자금이 부족할 것으로 보입니다. 소비 항목을 조정하거나 예비 자금을 늘리는 방안을 고려하세요.")
