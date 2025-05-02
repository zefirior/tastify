import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import * as React from "react";
import {FormControl} from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import SendIcon from "@mui/icons-material/Send";

export default function SubmissionForm({submitOption, setSubmitOption, nameOptions, optionBuilder, onClick}) {
    return(
        <>
            <FormControl fullWidth>
                <InputLabel id="demo-simple-select-label">Your suggestion</InputLabel>
                <Select
                    id="name-suggestion"
                    variant="outlined"
                    value={submitOption}
                    label="Choose one option"
                    onChange={(e) => setSubmitOption(e.target.value)}
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
