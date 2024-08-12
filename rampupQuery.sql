SELECT                                                                                                                      provider,                                                                                                         url,                                                                                             
    test_id,
    isCold,                                                                                          
    CAST(STRFTIME('%s', start) AS INTEGER) - CAST(STRFTIME('%s', MIN(start) OVER (PARTITION BY test_id)) AS INTEGER) AS second,
        waiting_ms
    FROM
        RampUp