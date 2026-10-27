# EDA rápido — UNSW-NB15

Fecha de auditoría: 2026-10-27.

## Integridad y esquema

| Partición | Filas | Columnas | SHA-256 verificado | Nulos |
|---|---:|---:|---|---:|
| UNSW_NB15_training-set.csv | 175,341 | 45 | sí | 0 |
| UNSW_NB15_testing-set.csv | 82,332 | 45 | sí | 0 |

Las dos particiones comparten esquema y contienen 45 columnas (30 enteras, 11 flotantes y 4 de texto).

## Variable objetivo

| Partición | Normal (0) | Ataque (1) | Proporción de ataques |
|---|---:|---:|---:|
| training | 56,000 (31.9%) | 119,341 (68.1%) | 68.1% |
| testing | 37,000 (44.9%) | 45,332 (55.1%) | 55.1% |

La proporción de ataques difiere entre entrenamiento y test; consérvese como observación de distribución, no como criterio para ajustar el modelo con test.

## Categorías de ataque

| Categoría | Entrenamiento | Test |
|---|---:|---:|
| Normal | 56,000 | 37,000 |
| Generic | 40,000 | 18,871 |
| Exploits | 33,393 | 11,132 |
| Fuzzers | 18,184 | 6,062 |
| DoS | 12,264 | 4,089 |
| Reconnaissance | 10,491 | 3,496 |
| Analysis | 2,000 | 677 |
| Backdoor | 1,746 | 583 |
| Shellcode | 1,133 | 378 |
| Worms | 130 | 44 |

## Variables categóricas frecuentes

### `proto`

- training: `tcp`: 79,946, `udp`: 63,283, `unas`: 12,084, `arp`: 2,859, `ospf`: 2,595
- testing: `tcp`: 43,095, `udp`: 29,418, `unas`: 3,515, `arp`: 987, `ospf`: 676

### `service`

- training: `-`: 94,168, `dns`: 47,294, `http`: 18,724, `smtp`: 5,058, `ftp-data`: 3,995
- testing: `-`: 47,153, `dns`: 21,367, `http`: 8,287, `smtp`: 1,851, `ftp`: 1,552

### `state`

- training: `INT`: 82,275, `FIN`: 77,825, `CON`: 13,152, `REQ`: 1,991, `RST`: 83
- testing: `FIN`: 39,339, `INT`: 34,163, `CON`: 6,982, `REQ`: 1,842, `ACC`: 4

## Duplicados y solapamiento

| Partición | Filas repetidas por predictores tras la primera | Grupos con etiquetas contradictorias |
|---|---:|---:|
| training | 74,301 | 229 |
| testing | 28,386 | 6 |

Hay 8,541 de 82,332 filas de test (10.37%) cuyo vector de predictores aparece también en entrenamiento. El cotejo excluye `id`, `label` y `attack_cat`.

Los grupos de predictores duplicados con etiquetas contradictorias requieren una política documentada antes de crear entrenamiento/validación. No se eliminan ni se resuelven automáticamente en este EDA. Al crear la validación desde entrenamiento, mantén cada grupo de predictores en una sola partición.

## Resumen numérico de entrenamiento

Cuantiles de las variables numéricas (sin `id` ni `label`):

| Variable | Mín. | Mediana | P75 | P95 | Máx. |
|---|---:|---:|---:|---:|---:|
| `dur` | 0 | 0.0016 | 0.6681 | 3.0795 | 60 |
| `spkts` | 1 | 2 | 12 | 64 | 9616 |
| `dpkts` | 0 | 2 | 10 | 62 | 10974 |
| `sbytes` | 28 | 430 | 1418 | 13662 | 1.29652e+07 |
| `dbytes` | 0 | 164 | 1102 | 39076 | 1.46556e+07 |
| `rate` | 0 | 3225.81 | 125000 | 333333 | 1e+06 |
| `sttl` | 0 | 254 | 254 | 254 | 255 |
| `dttl` | 0 | 29 | 252 | 252 | 254 |
| `sload` | 0 | 879675 | 8.88889e+07 | 2.66667e+08 | 5.988e+09 |
| `dload` | 0 | 1447.02 | 27844.9 | 4.07105e+06 | 2.24227e+07 |
| `sloss` | 0 | 0 | 3 | 12 | 4803 |
| `dloss` | 0 | 0 | 2 | 24 | 5484 |
| `sinpkt` | 0 | 0.2797 | 55.1569 | 245.213 | 84371.5 |
| `dinpkt` | 0 | 0.006 | 51.053 | 160.492 | 56716.8 |
| `sjit` | 0 | 0 | 2513.3 | 9505.48 | 1.46048e+06 |
| `djit` | 0 | 0 | 114.991 | 3054.77 | 289388 |
| `swin` | 0 | 0 | 255 | 255 | 255 |
| `stcpb` | 0 | 0 | 1.91665e+09 | 3.8142e+09 | 4.29496e+09 |
| `dtcpb` | 0 | 0 | 1.91367e+09 | 3.81302e+09 | 4.29488e+09 |
| `dwin` | 0 | 0 | 255 | 255 | 255 |
| `tcprtt` | 0 | 0 | 0.0655 | 0.1967 | 2.5189 |
| `synack` | 0 | 0 | 0.0233 | 0.1036 | 2.1004 |
| `ackdat` | 0 | 0 | 0.0389 | 0.0955 | 1.5209 |
| `smean` | 28 | 73 | 100 | 638 | 1504 |
| `dmean` | 0 | 44 | 89 | 786 | 1458 |
| `trans_depth` | 0 | 0 | 0 | 1 | 172 |
| `response_body_len` | 0 | 0 | 0 | 166 | 6.55806e+06 |
| `ct_srv_src` | 1 | 5 | 12 | 33 | 63 |
| `ct_state_ttl` | 0 | 1 | 2 | 2 | 6 |
| `ct_dst_ltm` | 1 | 2 | 7 | 24 | 51 |
| `ct_src_dport_ltm` | 1 | 1 | 5 | 22 | 51 |
| `ct_dst_sport_ltm` | 1 | 1 | 3 | 17 | 46 |
| `ct_dst_src_ltm` | 1 | 3 | 12 | 33 | 65 |
| `is_ftp_login` | 0 | 0 | 0 | 0 | 4 |
| `ct_ftp_cmd` | 0 | 0 | 0 | 0 | 4 |
| `ct_flw_http_mthd` | 0 | 0 | 0 | 1 | 30 |
| `ct_src_ltm` | 1 | 3 | 9 | 26 | 60 |
| `ct_srv_dst` | 1 | 4 | 12 | 33 | 62 |
| `is_sm_ips_ports` | 0 | 0 | 0 | 0 | 1 |

## Alcance y cautelas

- El objetivo para el modelo es `label`; excluye `label`, `attack_cat` e `id` de las entradas. `attack_cat` revela la respuesta e `id` sirve solo para auditoría y trazabilidad.
- No se han creado aquí particiones de validación ni transformaciones.
- El análisis del test se limita a auditoría descriptiva; sus etiquetas y métricas no deben guiar la elección del modelo o del umbral.
- Fuente de atribución oficial: [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset). Descarga usada: mirror de terceros fijado en un commit; las huellas SHA-256 verifican la copia del mirror, no la autenticidad del origen oficial.

La auditoría completa por columna, tipo y huella está en `auditoria_datos.json`.
