ltm policy uri-routing-policy {
    controls { forwarding asm }
    last-modified 2018-06-19:23:44:06
    requires { http }
    rules {
        uri_1 {
            actions {
                0 {
                    forward
                    select
                    pool f5demo-1
                }
                1 {
                    asm
                    enable
                    policy /Common/linux-high
                }
            }
            conditions {
                0 {
                    http-uri
                    path
                    starts-with
                    values { /static }
                }
            }
            ordinal 1
        }
        uri_2 {
            actions {
                0 {
                    forward
                    select
                    pool f5demo-2
                }
                1 {
                    asm
                    enable
                    policy /Common/linux-high
                }
            }
            conditions {
                0 {
                    http-uri
                    path
                    starts-with
                    values { /api }
                }
            }
            ordinal 2
        }
        default {
            actions {
                0 {
                    asm
                    enable
                    policy /Common/linux-high
                }
            }
            ordinal 3
        }
    }
    status legacy
    strategy first-match
}