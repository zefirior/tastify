import Button from "@mui/material/Button";
import * as React from "react";
import {FormControl} from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import SendIcon from "@mui/icons-material/Send";

export default function SubmissionForm({selectedKey, setSelectedKey, nameOptions, optionBuilder, onClick}) {
    console.log("selectedKey", selectedKey);
    return(
        <>
            <FormControl fullWidth>
                <InputLabel id="demo-simple-select-label">Your suggestion</InputLabel>
                <Select
                    id="name-suggestion"
                    variant="outlined"
                    value={selectedKey || ""}
                    label="Choose one option"
                    onChange={(e) => setSelectedKey(e.target.value)}
                >
                    {nameOptions.map((option) => optionBuilder(option))}
                </Select>
            </FormControl>

            <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                onClick={onClick}
            >
                Submit
            </Button>
        </>
    )
}
