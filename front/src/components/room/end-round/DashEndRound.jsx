import * as React from 'react';
import RoundSummary from './RoundSummary.jsx';
import ScoreTable from '../../ScoreTable.jsx';
import { RoundStage } from '../../../lib/backend.js';

export default function DashEndRound({room}) {
    const stage = room.state.currentRound.stage;
    
    return stage === RoundStage.END_ROUND ? <RoundSummary room={room} /> : <ScoreTable room={room} />;
}
