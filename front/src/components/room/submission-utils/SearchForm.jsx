import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import SearchIcon from "@mui/icons-material/Search";
import * as React from "react";

export default function SearchForm({textPrefix, searchName, setSearchName, onSearchCLick}) {
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
            <Button
                variant="contained"
                color="primary"
                endIcon={<SearchIcon />}
                size="small"
                onClick={onSearchCLick}
            >
                Search
            </Button>
        </>
    )
}