import matplotlib.pyplot as plt
import numpy as np

employee_schedule = [
    ("ML/AI инженеры", 0, 6),
    ("Специалисты по обработке данных", 0, 3),
    ("Data Scientist", 0, 9),
    ("Психологи", 3, 6),
    ("Консультанты по психологии", 3, 6),
    ("NLP-инженеры", 1, 6),
    ("DevOps-инженеры", 2, 6),
    ("Project Менеджер", 0, 6),
    ("Product Менеджер", 0, 6),
    ("Midl AI и ML инженеры", 4, 9),
    ("Midl DevOps инженер", 5, 9),
    ("Аналитик-Тестировщик", 2, 9),
    ("Психологи-консультанты", 4, 9),
    ("Маркетологи", 5, 9),
    ("Бухгалтер", 6, 9),
]

phases = [
    ("Подготовка данных и начальная разработка", 1, 2),
    ("Начальное обучение и настройка", 3, 4),
    ("Финальное обучение и тонкая настройка", 5, 6),
    ("Стабильная работа проекта", 7, 9)
]

months = np.arange(0, 10)
unique_colors = plt.cm.get_cmap('tab20', len(employee_schedule))

fig, ax = plt.subplots(figsize=(12, 7))
for i, (employee, start, end) in enumerate(employee_schedule):
    ax.plot([start, end], [i, i], color=unique_colors(i), lw=8, solid_capstyle="butt")

ax.set_yticks(np.arange(len(employee_schedule)))
ax.set_yticklabels([e[0] for e in employee_schedule])
ax.set_xticks(months)
ax.set_title("Работа сотрудников по месяцам")

for phase, start, end in phases:
    center = (start + end) / 2 - 0.5
    ax.annotate(phase, xy=(center, -1.5), ha='center', va='top', fontsize=6, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='none', facecolor='lightgrey'))

plt.xlim(0, 9)
plt.ylim(-2, len(employee_schedule))

plt.tight_layout()
plt.grid(visible=True, linestyle='--', linewidth=0.5, color='gray')
plt.savefig("employee_schedule.png", bbox_inches='tight')
plt.close()
