# PD IC 能否区分 Type-C 转 HDMI 线和带 HDMI 的 Hub？

## 结论

**可以区分。** USB PD IC 通过 USB PD 协议中的 VDM（Vendor Defined Message）通信，能够识别连接设备的类型，从而区分 Type-C 转 HDMI 线（适配器）和带 HDMI 接口的 Hub。

---

## 区分原理

### 1. Discover Identity 响应中的 Product Type 字段

当 PD IC（作为 DFP/Source）向连接的设备发送 `Discover Identity` 命令时，设备会在 ID Header VDO 中返回 **Product Type** 字段：

| 设备类型 | Product Type (UFP) | 说明 |
|---|---|---|
| Type-C 转 HDMI 线/适配器 | Alternate Mode Adapter (AMA) | 表示这是一个替代模式适配器 |
| 带 HDMI 的 Hub | Hub | 表示这是一个 USB Hub 设备 |

### 2. Discover SVIDs 响应

两种设备都会响应 `Discover SVIDs` 命令，返回它们支持的 SVID（Standard or Vendor ID）。虽然两者都可能返回 DisplayPort Alt Mode SVID（`0xFF01`），但结合 Product Type 可以做出区分。需要注意的是，Type-C 接口上的 HDMI 视频信号通常是通过 DisplayPort Alt Mode 传输，再由设备内部转换为 HDMI 信号输出的。

### 3. Discover Modes 响应

通过 `Discover Modes` 命令，可以进一步获取设备支持的具体模式信息：

- **Type-C 转 HDMI 适配器**：通常只支持 DP Alt Mode 输出，没有 USB 数据传输能力。
- **带 HDMI 的 Hub**：除了支持 DP Alt Mode 外，还支持 USB 数据传输（USB 2.0/3.0），并可能有多个下行端口。

---

## 具体区分方法

### 方法一：检查 Product Type

```
ID Header VDO (Discover Identity Response):
  Bits [29:27] — Product Type (UFP)

  AMA (Alternate Mode Adapter) = 101b  → Type-C 转 HDMI 线
  Hub                          = 001b  → 带 HDMI 的 Hub
```

### 方法二：检查 UFP VDO 中的设备能力

```
UFP VDO:
  - USB 最高速度 (USB Highest Speed)
  - Alternate Modes 支持情况

Hub 通常支持 USB 2.0/3.0 数据通信，而 AMA 一般不支持或仅支持有限的 USB 功能。
```

### 方法三：检查 AMA VDO（仅适配器返回）

Type-C 转 HDMI 适配器在 Discover Identity 响应中会返回 AMA VDO，其中包含：
- VCONN 供电需求
- VBUS 是否需要
- 替代模式的详细信息

Hub 设备不会返回 AMA VDO，而是返回 UFP VDO。

---

## VDM 通信流程示意

```
DFP (PD IC)                          UFP (设备)
    |                                    |
    |--- Discover Identity ------------->|
    |<-- ID Header VDO + Product VDOs ---|  ← 通过 Product Type 区分
    |                                    |
    |--- Discover SVIDs ---------------->|
    |<-- SVID List (如 0xFF01) ----------|
    |                                    |
    |--- Discover Modes (SVID) --------->|
    |<-- Mode VDO ----------------------|
    |                                    |
    |--- Enter Mode ------------------->|
    |<-- ACK ---------------------------|
```

---

## 实际应用场景

| 场景 | PD IC 的行为 |
|---|---|
| 检测到 AMA（Type-C 转 HDMI） | 直接进入 Alt Mode，输出视频信号；无需提供 USB 数据通道 |
| 检测到 Hub（带 HDMI） | 同时提供 USB 数据通道和 Alt Mode 视频输出（如果带宽允许） |

---

## 总结

PD IC 可以通过以下 USB PD 协议机制来区分 Type-C 转 HDMI 线和带 HDMI 的 Hub：

1. **Product Type 字段**：AMA vs Hub
2. **AMA VDO vs UFP VDO**：适配器返回 AMA VDO，Hub 返回 UFP VDO
3. **USB 数据能力**：Hub 支持 USB 数据传输，纯适配器不支持

这些信息均可通过标准的 USB PD Structured VDM 命令获取，无需额外的私有协议支持。

---

## 参考资料

- USB Power Delivery Specification, Revision 3.1
- USB Type-C Cable and Connector Specification, Revision 2.1
- VESA DisplayPort Alt Mode on USB Type-C Standard
