# freflow-modem

Modem for FreFlow glow stick

## !! Important notes !!

This software is developed for technical research on FreFlow glow stick.

This software uses devices connected to a computer to emit radio waves. It is recommended that you use it in accordance with your local laws and regulations.

## Summary

This software sends and receives (in progress) wireless messages for the FreFlow glow stick.

## Usage

### freflow-tx

```
$ freflow-tx --help

NAME
    freflow-tx - FreFlow Modem CLI

SYNOPSIS
    freflow-tx --dev=DEV --sr=SR --freq=FREQ --gain=GAIN <flags>

DESCRIPTION
    FreFlow Modem CLI

ARGUMENTS
    DEV
        TX Device
    SR
        TX Sampling Rate
    FREQ
        TX Frequency
    GAIN
        TX Gain (db)

FLAGS
    -p, --preamble_length=PREAMBLE_LENGTH
        Default: 48
        Preamble length in bytes
    -l, --log_level=LOG_LEVEL
        Default: 'INFO'
        Log level. Defaults to "INFO". {CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|NOTSET}
```

#### light

Light

```
$ freflow-tx light --help

NAME
    freflow-tx light - Light

SYNOPSIS
    freflow-tx light SELF RED GREEN BLUE <flags>

DESCRIPTION
    Light

POSITIONAL ARGUMENTS
    SELF
    RED
        Red (0-255)
    GREEN
        Green (0-255)
    BLUE
        Blue (0-255)

FLAGS
    -s, --system_id=SYSTEM_ID
        Default: 65535
        System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
    -c, --channel=CHANNEL
        Default: 255
        Channel (0x0000-0xFFFF). Defaults to 0xFF.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

#### light-interactive

Light (Interactive Mode)

```
$ freflow-tx light-interactive --help

NAME
    freflow-tx light-interactive - Light (Interactive Mode)

SYNOPSIS
    freflow-tx light-interactive SELF <flags>

DESCRIPTION
    Transmit message by enter a comma separated RGB (0-255) and a line break.

POSITIONAL ARGUMENTS
    SELF

FLAGS
    -s, --system_id=SYSTEM_ID
        Default: 65535
        System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
    -c, --channel=CHANNEL
        Default: 255
        Channel (0x0000-0xFFFF). Defaults to 0xFF.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

#### test-sig-err

Test Signal Error

```
$ freflow-tx test-sig-err --help

NAME
    freflow-tx test-sig-err - Test Signal Error

SYNOPSIS
    freflow-tx test-sig-err SELF <flags>

DESCRIPTION
    Green: No Error (0%)
    Blue: Few Error (0% < error <= 5%)
    Purple: Many Error (5% < error <= 20%)
    Red: Too Many Error (20% < error)

POSITIONAL ARGUMENTS
    SELF

FLAGS
    -s, --system_id=SYSTEM_ID
        Default: 65535
        System ID (0x0000-0xFFFF). Defaults to 0xFFFF.
    -c, --channel=CHANNEL
        Default: 255
        Channel (0x0000-0xFFFF). Defaults to 0xFF.

NOTESe
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

## List of verified FreFlow glow stick

- 堀江由衣ベストライブ～由衣と時間泥棒～ (Model unknown) - 2013
- 堀江由衣をめぐる冒険V～狙われた学園祭～ (Model unknown) - 2015

## Authors

- soltia48 (ソルティアよんはち)

## Thanks

- [monta](https://monta.moe.in/) - Wrote [a review article about FreFlow](https://monta.moe.in/wp/2013/05-09/23-56_1056)
- [kita♒](https://x.com/kita556) - Wrote [a initial analysis](https://x.com/kita556/status/333620995132903424)

## License

[MIT](https://opensource.org/license/MIT)

Copyright (c) 2024 soltia48 (ソルティアよんはち)
