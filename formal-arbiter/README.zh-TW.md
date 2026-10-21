# Round-Robin 仲裁器的 Formal 驗證

[English](README.md)

ICLAB Bonus Lab · 2026 春季 · SystemVerilog Assertions · JasperGold Formal

待測設計是課程提供、藏有一個 bug 的 8 個 requester round-robin 仲裁器，連同已經 bind 好的 checker 範本和輸入 assume。我補完缺少的 cover 和 assert，用 JasperGold 執行，再從失敗的 assertion 找出 bug。

## 方法

| Property 類型 | 作用 | 這個 lab 裡的例子 |
| --- | --- | --- |
| `assume`（課程提供） | 限制輸入環境 | request 拉高後，在被 grant 之前不會放掉 |
| `cover` | 確認某個情境做得出來，代表 assume 沒有把設計限制死 | 連續 8 個 cycle 依序 grant 給 requester 0 → 1 → … → 7（bound 8 達成）；requester 1 被 grant 後，requester 0 可以等 6 個 cycle，但等不到 7 個（證明不可達） |
| `assert` | 在所有可達狀態下都必須成立 | 某個 grant 為高時其他全為低；同一時間最多一個 grant（`$countones`） |

刻意先寫 cover。如果 assume 寫得太嚴，所有 assertion 都會「空洞地通過」（vacuous pass）；cover 能達到，才證明有意義的行為還在。

## Fairness bug

8 個 requester 的 round-robin 公平性，代表等待中的 request 一定會在 8 個 cycle 內被服務：

```systemverilog
assert property (req[0] |-> ##[0:7] gnt[0]);
```

JasperGold 回傳一個反例：當 requester 0 是上一個被服務的 client，而且只有它在 request 時，它永遠拿不到 grant。優先權迴圈只掃 offset 1 到 N−1（`j < N`），漏掉上一個被服務的 client；沒有 grant 時上次服務的指標也不會更新，仲裁器因此死鎖。修正方式是改成 `j <= N`，讓上一個被服務的 client 以最低優先權被檢查。

## 心得

- Formal 會窮舉所有合法的輸入序列，對小模組能抓到 directed 或 random 模擬可能錯過的 corner case。
- 反例是最短長度的波形，比在很長的模擬裡找錯快得多。
- Cover property 是防止 assume 過度限制、產生錯誤信心的保險。

---

因為課程會沿用這個題目，checker 原始碼不公開。面試需要時可以提供。
