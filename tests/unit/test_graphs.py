from signals_lib.detailedGeneration import consolidateSignals


def test_consolidateSignals():
    df_test = consolidateSignals("AAPL")
    desired_date = '2020-01-02'
    result_df = df_test[df_test['Date'] == desired_date]

    expected_vol = 33911800
    assert result_df['Volume'].values[0] == expected_vol


if __name__ == '__main__':
    test_consolidateSignals()