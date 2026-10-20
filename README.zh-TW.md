# 數位 IC 設計作品集 — 林文遠

[English](README.md)

國立陽明交通大學電子研究所碩士生（數位系統組）。
這個 repo 整理 **2026 春季 ICLAB（積體電路設計實驗）** 的代表性專案，說明每個設計在做什麼、背後的架構取捨，以及最後達到的結果。

| 專案 | 重點 | 亮點 |
| --- | --- | --- |
| [雙核 16-bit RISC CPU](dual-core-cpu/README.zh-TW.md) | RTL → GDSII、記憶體系統、低功耗 | 3 個 AXI4 master、write-through D-cache、跨核記憶體存取順序、SRAM 從 3 顆減到 1 顆壓 peak power、Innovus APR 通過 DRC／LVS |
| [三時脈域加速器](cdc-accelerator/README.zh-TW.md) | 跨時脈域（CDC） | Handshake 同步器加 3 組 Gray code 指標的 async FIFO、SDRAM 命令控制器、JasperGold CDC 驗證 |
| [Round-Robin 仲裁器 Formal 驗證](formal-arbiter/README.zh-TW.md) | Assertion-based formal | SVA 的 assume／cover／assert，從反例波形找出 fairness bug |

**工具流程：** VCS（RTL、gate-level、post-layout 模擬）→ Design Compiler（`compile_ultra`）→ PrimeTime PX（功耗）→ Cadence Innovus（APR）→ JasperGold（formal、CDC）。製程為 UMC 180 nm standard cell。

## 這個 repo 放了什麼、沒放什麼

這裡只有我自己寫的說明文件和輔助腳本。

刻意**沒有**放的東西：

- **RTL 原始碼**：ICLAB 每學期會沿用作業題目，所以不公開完整解答。面試需要時可以提供。
- **課程教材**：spec、testbench、加密的 pattern，著作權屬於課程團隊。
- **製程與記憶體編譯器檔案**：standard cell library、SRAM model、netlist、SDF、layout，受晶圓廠 NDA 規範。

## 聯絡方式

nycumonkyking.ee11@nycu.edu.tw
