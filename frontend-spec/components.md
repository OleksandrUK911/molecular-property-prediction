# UI Components

## SmilesInput
Текстове поле (single-line) + кнопка "Predict" праворуч (під кнопкою — на
мобільному). Плейсхолдер: `e.g. CC(=O)Oc1ccccc1C(=O)O`. Enter в полі === клік
Predict. Disabled під час Loading (див. [predict-page.md](predict-page.md)).

## ExampleChips
Ряд з 3 клікабельних "chip"-кнопок: Aspirin, Caffeine, Ibuprofen. Кожна несе
захардкоджений SMILES. Клік → заповнює `SmilesInput` і одразу викликає submit
(без додаткового кліку на Predict).

## MoleculeStructure
Відображає SVG, отриманий з поля відповіді бекенду (RDKit-рендер). Квадратна
картка ~240×240px, зображення центроване, background — нейтральний
(картка, не прозорий). Клік → модалка зі збільшеним зображенням (P2, окремо
від MVP).

**Fallback-стан:** якщо поле SVG відсутнє/помилка рендеру — показати
placeholder-іконку молекули + текст "Structure preview unavailable" замість
порожнього блоку.

## ResultsCard
Вертикальний список полів (точні назви полів API — див.
[../backend-spec/api-contract.md](../backend-spec/api-contract.md)):
1. Заголовок: назва передбачуваної властивості + значення + одиниці
   (напр. "Predicted solubility: −2.31 log(mol/L)", з `predicted_target`)
2. Розділювач
3. Список дескрипторів (label: value), з об'єкта `descriptors`:
   MolWt, LogP, TPSA, NumHDonors (H-Bond Donors), NumHAcceptors
   (H-Bond Acceptors), NumRotatableBonds (Rotatable Bonds), RingCount
   (Num Rings) — усі 7 полів, ярлики UI людяні, ключі як в API
4. (P2, опційно) Confidence badge — з поля `confidence` (null для baseline
   моделі — бейдж не показується, поки модель не підтримує uncertainty).
   Кольоровий бейдж поруч із заголовком:
   зелений (high confidence / у межах applicability domain), жовтий (помірна
   невизначеність), без бейджа якщо модель не підтримує uncertainty.

## ErrorBanner
Горизонтальний банер під `SmilesInput`, червона/попереджувальна колірна
схема, іконка попередження + текст повідомлення. Для помилки "server
unavailable" — додатково кнопка "Retry" праворуч у банері.

## HistoryTable
Див. повний опис колонок і станів у [history-page.md](history-page.md).

## Skeleton-компоненти
- `ResultsSkeleton` — прямокутник на місці структури + кілька сірих рядків на
  місці картки результатів, використовується як Loading-стан Predict page.
- `TableRowSkeleton` — сірий рядок таблиці, для Loading-стану History page.
