# Clock Gating 低功耗加速器與 Sequential Equivalence Checking

[English](README.md)

ICLAB Lab 08 · 2026 春季 · UMC 180 nm · Design Compiler · PrimeTime PX · JasperGold SEC

**成果：** 通過所有檢查，包含 gate-level 模擬和兩次 JasperGold SEC。加上 clock gating 後總功耗降低 **36%**，從 4.30 mW 降到 2.74 mW。分數 92.77，排名 **31 / 145**。

## 設計內容

這個加速器對 4 × 4 矩陣做兩級 coupling layer 運算（類似可逆神經網路），支援兩種任務：

- **Forward：** 每一級做兩次矩陣乘法，一次取 mod 15 再加 1，另一次取 mod 256。接著做 element-wise（Hadamard）乘法和 bitwise XOR。
- **Backward：** 把相同的步驟倒過來做，乘法改成 element-wise 除法。

輸入在 97 個 cycle 內逐筆送進來，兩個 4 × 4 的結果在 32 個 cycle 內連續輸出。

限制條件：

- clock 固定 15 ns
- latency 不超過 200 cycles
- cell area 不超過 600,000 µm²
- 不能用 memory 和 DesignWare IP
- 除了 clock gating 用的 latch，不能有其他 latch

## Clock gating

同一個設計寫兩個版本：

- `LAB8_DESIGN_wocg`：沒有 clock gating
- `LAB8_DESIGN`：用 `GATED_OR` clock gating cell 控制暫存器的 clock，由 `cg_en` 輸入決定開或關

兩版除了 gating 的部分，其他程式碼必須完全相同。規格要求開啟 gating 後功耗至少降低 10%。

概念很簡單：不會改變值的暫存器就不需要 clock edge。像這樣的設計，大部分暫存器只有在特定階段才需要寫入，例如收輸入、某一級運算、或輸出。在其他階段把它們的 clock 關掉，就省下了原本每個 cycle 都會消耗的 clock 和 flip-flop 內部功耗。

| | 沒有 gating | 有 gating |
| --- | --- | --- |
| 總功耗（PTPX） | 4.30 mW | 2.74 mW（−36%） |

這個 lab 的評分指標是 latency × power² × area，所以功耗的影響被算了兩次。

## 證明兩個版本等價

模擬只能證明加了 gating 的設計能通過測資，沒辦法證明它在所有情況下都和原本的設計行為一致。

所以我用 JasperGold 做 **sequential equivalence checking（SEC）**，用 formal 方法證明兩個 RTL 版本的 `out_valid` 和 `out_data` 在任何輸入序列下都相同。

Formality 或 Conformal LEC 這類 combinational equivalence checker，需要兩邊的暫存器能一對一對應。但 clock gating 會改變暫存器更新的時間點，所以要改用 sequential 的證明。兩次 SEC 都通過，兩條輸出 assertion 都 proven。

## 學到的東西

- **Gated clock 的 fanout：** 一個 gated clock 不能帶太多 flip-flop。gating 訊號的 fanout 太大時，可能 RTL 模擬通過，gate-level 模擬卻出現 unknown（X）。
- **Equivalence checking：** 只要是「不應該改變功能」的修改，像 clock gating、retiming 或 ECO，都適合用 equivalence checking 確認。

---

RTL、規格、測資和 library 檔案都不公開（請見 [repo 首頁說明](../README.zh-TW.md)）。
