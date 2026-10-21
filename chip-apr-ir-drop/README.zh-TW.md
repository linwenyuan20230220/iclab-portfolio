# 晶片層級 APR 與 IR Drop 修正

[English](README.md)

ICLAB Lab 12 · 2026 春季 · UMC 180 nm · Cadence Innovus · Rail analysis

這個 lab 只做後端：我把自己 **Lab 05 設計**（W4A8 的 diffusion model 去噪加速器）的合成 netlist，做成一顆有 I/O pad ring、SRAM macro、電源網路，且通過 sign-off 檢查的完整晶片。接著對 layout 做 power 和 rail analysis，修正找到的 IR drop。

## 被擺放的設計

Lab 05 的加速器對 64 × 64 的灰階影像做 1 到 7 次去噪。每次迭代包含 down-sampling convolution、transformer block（self-attention 和 feed-forward network）、up-sampling convolution 和內插。權重 4-bit、activation 8-bit，兩者都存在晶片上的 SRAM，所以 floorplan 要容納好幾顆 hard macro。

## 流程

1. **I/O 規劃：** 撰寫 `CHIP.io` 和 pad shell。共 9 組 core power pad（右側 3 組，其他每邊 2 組）、4 組 I/O power pad（每邊 1 組）和 corner pad，core power pad 避開角落。
2. **Floorplan：** 每一邊 core 到 I/O 的距離都大於 100 µm，所有 SRAM 都放在 core 裡。
3. **Power plan：** core ring 線寬 9 µm，每邊用 wire group 加 interleaving、至少 5 組；水平與垂直 stripe 間距不超過 200 µm。
4. **Place、CTS、route：** 時脈 14.6 ns，post-route 最佳化後 setup 和 hold slack 都非負，DRV 為 0。
5. **驗證：** 加完 core filler 後 geometry（DRC）和 connectivity（LVS）都沒有錯誤；post-layout 模擬沒有 timing violation，latency 和 gate-level 相同，通過 lab demo。
6. **Power 與 rail analysis：** 在 Innovus 裡畫出整個 core 的 IR drop 分布。

## IR drop 的修正

Sign-off 標準是最大 IR drop 不超過 50 mV。第一次 rail analysis 量到 **70 mV**，集中在 core 的某一側。做了三項修改後降到 **43 mV**，符合標準：

| 修改 | 為什麼有效 |
| --- | --- |
| 在壓降最嚴重的那一側加 core power pad（那一側現在有 3 組） | 縮短電源到熱點區域的電流路徑 |
| 確保相鄰 SRAM 之間至少有兩條水平 stripe | Macro 會擋住原本規律的 stripe，夾在中間的 cell 只能靠又長又窄的路徑供電 |
| 把 SRAM 移到靠近 core 邊界的位置 | 讓耗電最大的元件貼近 power ring，而不是在 core 正中間 |

心得：SRAM macro 同時是大電流負載，也是電源網路的障礙物。它們放在哪裡，就決定電源網路哪裡最弱，所以 macro 擺放和 stripe 規劃必須一起考慮。

---

Layout、netlist 和截圖含有晶圓廠 library 資料，因此不公開。面試需要時可以說明細節。
