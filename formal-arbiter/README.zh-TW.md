# Round-Robin 仲裁器的 Formal 驗證

[English](README.md)

ICLAB Bonus Lab · 2026 春季 · SystemVerilog Assertions · JasperGold Formal

待測設計是課程提供的 8 個 requester 的 round-robin 仲裁器。我寫了一個由 SVA property 組成的 checker module，用 `bind` 掛到設計上，再用 JasperGold 探索並證明它的行為。

## 方法

| Property 類型 | 作用 | 這個 lab 裡的例子 |
| --- | --- | --- |
| `assume` | 限制輸入環境 | request 拉高後，在被 grant 之前不會放掉 |
| `cover` | 確認某個情境做得出來，代表 assume 沒有把設計限制死 | 連續 8 個 cycle 依序 grant 給 requester 0 → 1 → … → 7；兩次 grant 給 requester 0 之間，所有 request 都拉高 |
| `assert` | 在所有可達狀態下都必須成立 | 某個 grant 為高時其他全為低；同一時間最多一個 grant（`$countones`） |

刻意先寫 cover。如果 assume 寫得太嚴，所有 assertion 都會「空洞地通過」（vacuous pass）；cover 能達到，才證明有意義的行為還在。

## Fairness bug

8 個 requester 的 round-robin 公平性，代表等待中的 request 一定會在 8 個 cycle 內被服務：

```systemverilog
assert property (req[0] |-> ##[0:7] gnt[0]);
```

JasperGold 回傳一個反例：在某個 request 組合下，requester 0 等了超過 8 個 cycle。從反例波形定位到設計裡跳過 requester 0 的條件，並提出 RTL 的修正方式。

## 心得

- Formal 會窮舉所有合法的輸入序列，對小模組能抓到 directed 或 random 模擬可能錯過的 corner case。
- 反例是最短長度的波形，比在很長的模擬裡找錯快得多。
- Cover property 是防止 assume 過度限制、產生錯誤信心的保險。

---

因為課程會沿用這個題目，checker 原始碼不公開。面試需要時可以提供。
