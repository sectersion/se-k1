[sek1v1_bom.csv](https://github.com/user-attachments/files/26492156/sek1v1_bom.csv)# Secure Element K1

This project is a small hardware password vault and crypto cold wallet using an ESP32-S3, a TPM (SLB9670), and a W25Q-series SPI flash chip.  

I created this project because a family member was talking about crypto wallets, and it gave me the idea of password managers. Online password managers are tied to one login and if that gets breached, all your accounts are gone. This implements a secure way to hold passwords, fully offline, not relying on cloud providers like Google.

## Features

- ESP32-S3 with USB HID keyboard output  
- TPM-backed master key for decrypting stored passwords  
- External SPI flash for record storage (ID, encrypted password, hashed PIN, MAC)  
- Button-based keypad input  
- PIN verification using SHA-256 with device-unique salt  
- Short-lived in-memory plaintext handling

## System

1. User enters a 4-digit record ID.  
2. Device loads the corresponding record from flash.  
3. User enters a 6-digit PIN.  
4. PIN is hashed and compared to the stored hash.  
5. If valid, the TPM unseals the master key.  
6. The encrypted password is decrypted using the TPM-provided key.  
7. The password is typed over USB HID.  
8. Plaintext is cleared.

## Components

| Designator | Footprint | Quantity | Value | LCSC Part # |
|---|---|---|---|---|
| 3V3 | TestPoint_Pad_D1.0mm | 1 | 3V3 | |
| 5V | TestPoint_Pad_D1.0mm | 1 | 5V | |
| BT1 | BatteryHolder_Renata_SMTU2032-LF_1x2032 | 1 | SMTU2032-LF | C18212226 |
| C1, C3, C7 | 0402 | 3 | 10uF | C315248 |
| C2 | CP_Elec_6.3x5.8 | 1 | 10uF | C128459 |
| C4 | 0402 | 1 | 0.1uF | C60474 |
| C5, C6 | 0402 | 2 | 100nF | C60474 |
| C8 | 0805 | 1 | 100nF | C49678 |
| D1 | D_SMA | 1 | SS14 | C2837270 |
| J1 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | 1 | USB_C_Receptacle_USB2.0_14P | C2765186 |
| R1, R2 | 0402 | 2 | 5.1k | C105872 |
| R3, R4, R5, R6, R8 | 0402 | 5 | 10k | C60490 |
| RST | SW_TS-1088-AR02016 | 1 | TS-1088-AR02016 | C720477 |
| RXD | TestPoint_Pad_D1.0mm | 1 | RX | |
| S1 | SW_TS-1088-AR02016 | 1 | 1 | C720477 |
| S2 | SW_TS-1088-AR02016 | 1 | 4 | C720477 |
| S3 | SW_TS-1088-AR02016 | 1 | 7 | C720477 |
| S4 | SW_TS-1088-AR02016 | 1 | 2 | C720477 |
| S5 | SW_TS-1088-AR02016 | 1 | 5 | C720477 |
| S6 | SW_TS-1088-AR02016 | 1 | 8 | C720477 |
| S7 | SW_TS-1088-AR02016 | 1 | 3 | C720477 |
| S8 | SW_TS-1088-AR02016 | 1 | 6 | C720477 |
| S9 | SW_TS-1088-AR02016 | 1 | 9 | C720477 |
| S10 | SW_TS-1088-AR02016 | 1 | 0 | C720477 |
| TXD | TestPoint_Pad_D1.0mm | 1 | TX | |
| U1 | ESP32-S2-MINI-1U | 1 | ESP32-S3-MINI-1U | C2980299 |
| U2 | QFN50P500X500X90-33N | 1 | SLM9670AQ20FW1311XTMA1 | C2651754 |
| U3 | SOIC127P790X216-8N | 1 | W25Q16JVSSIQ | C82317 |
| U4 | SOT-223-3_TabPin2 | 1 | AMS1117-3.3 | C6186 |



## Record Format

Each stored record contains:

- id: 4 bytes  
- encrypted_password: fixed length  
- encrypted_pin: 16-byte truncated SHA-256 hash  
- mac: record integrity field

## Pictures
3D model:
<img width="588" height="446" alt="image" src="https://github.com/user-attachments/assets/c29b3451-7981-4a6e-948b-6828111b88c1" />

PCB:
<img width="1218" height="844" alt="image" src="https://github.com/user-attachments/assets/3b9fe9f3-f634-4a09-9991-75febcfa3e37" />


