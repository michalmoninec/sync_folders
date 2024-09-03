# Synchronization project - pre-interview task

Script to sync two folders to be identical copies

### Dependencies

```bash
pip install -r requirements.txt
```

### Run script

```bash
python main.py --src_root_path --rep_root_path --log_dir_path --sync_interval
```

## Script Parameters:

`--src_root_path`

-   **Required**: Yes
-   **Type**: `str`
-   **Description**: Specifies the path of source folder. Must be valid dir.
-   **Example**: `../src`

`--rep_root_path`

-   **Required**: Yes
-   **Type**: `str`
-   **Description**: Specifies the path of source folder. Must be valid dir.
-   **Example**: `../rep`

`--log_dir_path`

-   **Required**: Yes
-   **Type**: `str`
-   **Description**: Specifies the path of source folder. Cannot be in source or replica directory.
-   **Example**: `../log`

`--sync_interval`

-   **Required**: Yes
-   **Type**: `int`
-   **Description**: Specifies the syncing interval in seconds.
-   **Example**: `10`

### Run tests

```bash
pytest [-v] [-s] to test
```
