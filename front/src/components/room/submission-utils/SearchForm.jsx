import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import SearchIcon from "@mui/icons-material/Search";
import * as React from "react";
import CloseIcon from "@mui/icons-material/Close";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";

export default function SearchForm({textPrefix, searchName, setSearchName, onSearchCLick, skipBtn, onSkipBtnClick}) {
    return(
        <>
            <Box display="flex" alignItems="center">
                <span>{textPrefix}</span>
                <TextField
                    id="name-search"
                    label="Start typing..."
                    variant="standard"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                    sx={{ marginLeft: 1 }}
                />
            </Box>

            <Stack direction="row" spacing={2}>
                <Button
                    variant="contained"
                    color="primary"
                    endIcon={<SearchIcon/>}
                    size="small"
                    onClick={onSearchCLick}
                >
                    Search
                </Button>

                {skipBtn && (
                    <IconButton
                        aria-label="skip-track"
                        variant="contained"
                        color="error"
                        onClick={onSkipBtnClick}
                    >
                        <CloseIcon/>
                    </IconButton>
                )}
            </Stack>
        </>
    )
}