# 實體設計演算法（C++）

[English](README.md)

陽明交大 Physical Design Automation（研究所課程）· 2026 秋 · C++17 · 單執行緒 · Linux

三份程式作業，每一份都是獨立的 C++ 工具：讀入設計、解一個實體設計的核心問題、輸出結果，再由官方 verifier 檢查。

| Lab | 問題 | 方法 |
| --- | --- | --- |
| [1](#lab-1--corner-stitching) | 佈局資料結構：tile plane 的 point finding 與鄰居查詢 | Corner stitching，space tile 維持最大水平條帶 |
| [2](#lab-2--異質-3d-ic-partitioning) | 把最多 10 萬顆 cell 分到上下兩層 die，最小化跨 die 的 net | Multilevel hypergraph partitioning 加有限制的 FM refinement |
| [3](#lab-3--fixed-outline-floorplanning) | 在固定外框內擺放最多 200 個 block，滿足限制下最小化 wirelength | B\*-tree 模擬退火，再做合法化與局部搜尋 |

---

## Lab 1 — Corner Stitching

**問題：** 在最大 200,000 × 200,000 的外框內，為最多 25,000 個互不重疊的矩形 block 建立佈局平面。插入過程中要回答 point finding 查詢，最後輸出每個 block 碰到幾個 block tile 和 space tile。

Space tile 必須一直維持**最大水平條帶**：左右不能相鄰另一個 space tile，而且要盡量寬。

**方法：**
- 每個 tile 記錄座標和四個 stitch（右上、上右、左下、下左），所有操作都沿著 stitch 在局部移動，不必掃描全部 tile。
- **Point finding：** 從上一次停留的 tile 出發，先垂直走到正確的列，再水平移動，重複直到找到包含該點的 tile。
- **插入 block：**
  1. 在 block 的上下邊切開 space tile。
  2. 由上往下，把 block 經過的每個 space tile 切成左、中、右三塊。
  3. 中間的部分合併成一個 block tile。
  4. 左右剩下的 space tile 只要能對齊就垂直合併，恢復最大條帶的性質。
- **鄰居列舉：** 沿著 block 的每一條邊順著 stitch 走一圈。

---

## Lab 2 — 異質 3D IC Partitioning

**問題：** 把 netlist 視為 hypergraph（最多 10 萬顆 cell、20 萬條 net），把每顆 cell 分到上層或下層 die。兩層 die 使用不同的 standard cell library，所以同一顆 cell 在兩層的面積不同。
- **目標：** 最小化跨兩層的 net 數。
- **硬性限制：** 每層 die 的面積上限，以及 cell 數的平衡範圍。
- **時間限制：** 每個測資 60 秒。

**方法（multilevel partitioning，概念類似 hMETIS）：**
1. **Coarsening：** 逐層把連接緊密的 cell 合併成 cluster，直到剩下約 150 個節點。每個 cluster 的 cell 數和在兩層的面積都有上限，讓粗化後的問題仍然可解。計算 cluster 分數時忽略超大的 net，因為它們幾乎不反映局部性。
2. **社群導引：** 部分嘗試會先對 hypergraph 的 clique expansion 跑 Louvain 社群偵測，讓 coarsening 盡量留在同一個社群內。大 net 改用環狀展開，避免記憶體爆掉。
3. **初始分割：** 在最粗的那一層做多次隨機嘗試。目標刻意放在平衡範圍的邊界，因為兩邊略不平均時，通常切到的 net 比較少。
4. **Uncoarsening 加 FM refinement：** Fiduccia–Mattheyses 演算法用 gain bucket 選擇移動。移動時允許短暫超出限制最多一顆 cell，每一輪結束後回溯到最好的那一步，先比限制違反量，再比 cut 數。
5. **V-cycle：** 以目前最佳解為基礎重新粗化，並輪流使用不同策略。在 20 秒預算內保留最好的合法解。如果一直找不到合法解，就改用依 cell 種類的貪婪分配當保底。

**成果：** 成績 94.89 / 100，全班排名 6 / 82，7 個隱藏測資中有 2 個是全班最小的 cut size。

---

## Lab 3 — Fixed-Outline Floorplanning

這題是 ICCAD 2026 CAD Contest Problem C（Intel 的 *FloorSet Challenge*）的簡化版。

**問題：** 在給定外框內，不重疊地擺放最多 200 個 block。Block 分三種：
- **Soft：** 只給面積，形狀自己決定，面積誤差 1% 內、長寬比不超過 3。
- **Fixed-shape：** 給定長寬。
- **Preplaced：** 連位置都給定。

目標是 block 與 block、block 與邊界 terminal 之間，以質心計算的加權 Manhattan wirelength。另有兩種計分限制：
- **MIB 群組：** 同一群的 soft block 形狀必須相同。
- **邊界與角落限制：** block 必須貼齊指定的邊或角。

時間限制為單執行緒 120 秒。

**方法：**
1. **Soft block 形狀：** 每種面積先列出面積最小（約 0.99 倍目標面積）的合法整數形狀，再取樣約 40 種長寬比。同一個 MIB 群組共用同一個形狀編號，所以 **MIB 限制在設計上一定滿足**。
2. **保底解：** 先用建構式的 legalizer 產生合法 floorplan。有邊界限制的 block 先放到指定邊上，其餘用 skyline best-fit 擺放，soft block 可以調整成剛好填滿空隙的寬度。
3. **B\*-tree 模擬退火加 contour packing：**
   - Contour 用 linked list 實作，每個 block 的 packing 均攤 O(1)。
   - Preplaced block 也是樹的節點；和它重疊時給懲罰，而不是硬推開，讓緊的測資比較容易搜尋。
   - 成本函數為 wirelength / 門檻 + 超出外框量 + 邊界懲罰。
   - 先重複做多輪 warm 降溫找到合法解，再切換成以 wirelength 為主的退火。
   - **提早拒絕：** 先抽出接受門檻，packing 時一旦超出外框量已經超過門檻就提早停止。
   - 接近合法的解，會把凸出或重疊的 block 塞進內部空洞來修補。
4. **修補與優化：**
   - 位置空著時，把 block 推到它被要求貼齊的邊上。
   - 降低 wirelength 的方法：把 block 往連線的加權中位數滑動、交換同尺寸的 block、原地調整 soft block 的形狀。
5. **Large-neighborhood search：** 在絕對座標下做 ruin-and-recreate，其中包含一個專門清出指定邊空間的移動。只有在 wirelength 落入計分區間時，才會用一個邊界限制換取 wirelength。
6. **挑選與自我檢查：** 用真正的計分公式挑出最後的解，輸出前重新檢查全部 8 條合法性規則。質心可能落在半格上，所以 wirelength 用兩倍的整數座標精確計算。

**公開測資結果（50 個 block）：** 合法 floorplan，10 個邊界限制與 4 個 MIB 群組全部滿足，wirelength 289,294.5，比助教參考值 286,355.5 高約 1.0%。在課程工作站上的 verifier 分數為 18.97 / 20。

---

原始碼不公開：課程會比對同學之間的程式相似度，作業也會沿用。面試時可提供。
