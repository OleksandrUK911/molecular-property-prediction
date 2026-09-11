# Design system

Мінімальна дизайн-система для MVP-масштабу проєкту (не повноцінна UI-kit
бібліотека) — достатньо токенів, щоб верстати консистентно без рішень на льоту.

## Кольори

| Токен | Light | Dark | Використання |
|---|---|---|---|
| `bg` | `#ffffff` | `#0f1115` | фон сторінки |
| `surface` | `#f5f6f8` | `#1a1d23` | картки (ResultsCard, MoleculeStructure) |
| `border` | `#e2e4e8` | `#2a2e37` | межі карток, роздільники |
| `text` | `#1a1d23` | `#e8e9ec` | основний текст |
| `text-muted` | `#6b7280` | `#9aa0ab` | підписи, другорядний текст |
| `accent` | `#2563eb` | `#3b82f6` | кнопка Predict, активна навігація, бари графіка |
| `success` | `#16a34a` | `#22c55e` | confidence badge "high" |
| `warning` | `#d97706` | `#f59e0b` | confidence badge "moderate" |
| `error` | `#dc2626` | `#ef4444` | ErrorBanner, невалідні поля |

Контраст `text`/`text-muted` на відповідному `bg`/`surface` мусить проходити
WCAG AA (4.5:1 для звичайного тексту) — перевірити обидві теми перед релізом
(пункт з `TODO/frontend/TODO_accessibility_responsive.md`).

## Типографіка

| Роль | Розмір / вага | Використання |
|---|---|---|
| `heading` | 24px / 600 | заголовки сторінок ("Predict molecular properties") |
| `subheading` | 16px / 600 | заголовки секцій (About page) |
| `body` | 14px / 400 | основний текст, значення дескрипторів |
| `caption` | 12px / 400 | timestamps, підписи в таблицях |

Шрифт: системний stack (`-apple-system, "Segoe UI", Roboto, sans-serif`) —
без підключення веб-шрифту, щоб не ускладнювати MVP.

## Spacing

Крок 4px: `4, 8, 12, 16, 24, 32, 48`. Картки — внутрішній відступ 16px,
відступ між секціями сторінки — 24px, між сторінкою і краєм viewport — 16px
(мобільний) / 24px (desktop).

## Border radius
`8px` для карток і кнопок, `4px` для чипів/бейджів.

## Стани інтерактивних елементів
- **Кнопка Predict:** default (`accent`) → hover (темніше на 10%) → disabled
  (сірий `text-muted` на `surface`, курсор not-allowed) під час Loading.
- **Input:** default border `border` → focus border `accent` + outline
  (для клавіатурної навігації, узгоджено з a11y-задачею tab-порядку) →
  error border `error` (коли показано ErrorBanner).
- **Chips (ExampleChips):** default `surface` фон → hover `border` фон →
  active/pressed `accent` з білим текстом.

### Залежності
- Реалізує токени контрасту для `TODO/frontend/TODO_accessibility_responsive.md`
  (WCAG AA, dark/light тема).
- Кольори confidence badge узгоджені з `data-visualization.md` (індикатор впевненості).
