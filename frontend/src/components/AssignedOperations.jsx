import React, { useEffect, useState, useContext } from "react";
import {
	Typography,
	Box, Stack, Grid,
	Accordion, AccordionSummary, AccordionDetails,
	Pagination
} from "@mui/material";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useNavigate } from "react-router-dom";

import ToothMarks from "./ToothMarks";
import operationService from "../servicies/OperationService";
import AuthContext from '../context/AuthContext';
import ModalSetOperStatus from "../modals/ModalSetOperStatus";


const AssignedOperations = () => {
	const { authTokens } = useContext(AuthContext);
	const [operations, setOperations] = useState([]);
	const [operationStatuses, setOperationStatuses] = useState([]);
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);

	const navigate = useNavigate();

	const getOperations = (page) => {
		operationService.getForTech(page)
			.then(res => {
				setOperations(res.data.results);
				setTotalPages(res.data.totalPages);
			})
			.catch(err => console.log(err));
	}

	useEffect(() => {
		if (!authTokens || !authTokens.access) {
			navigate('/login');
			return;
		}

		operationService.getOperationStatuses()
			.then(res => {
				let operations = res.data.map(oper => { return { key: oper.id, value: oper.name } });
				setOperationStatuses(operations);
			})
			.catch(err => console.log(err));

		getOperations(page);
	}, [])

	const handleChangePage = (_, newPage) => {
		setPage(newPage);
		getOperations(newPage);
	}

	const formatExecTime = (execTime) => {
		const hours = Number(execTime.substring(0, 2));
		const minutes = Number(execTime.substring(3, 5));
		if (hours === 0) {
			return <>{minutes} мин.</>;
		}
		return <>
			{hours} ч. {minutes} мин.
		</>
	}

	const formatExecStartDateTime = (execStart) => {
		return <>
			{execStart.substring(0, 10)} {execStart.substring(11, 16)}
		</>
	}

	const renderOperations = () => {
		return operations.map((oper) => (
			<Accordion>
				<AccordionSummary
					expandIcon={<ExpandMoreIcon />}
					aria-controls="panel1-content"
					id="panel1-header"
				>
					<Stack>
						<Typography item>Вид операции: {oper.operationType.name}</Typography>
						<Typography item>Статус операции: {oper.operationStatus.name}</Typography>
						{
							oper.execStart ? <Typography item>Назначено на: {formatExecStartDateTime(oper.execStart)}</Typography>
								: <Typography item>Дата и время начала выполнения не указаны</Typography>
						}
						<Typography item>
							На выполнение: {formatExecTime(oper.operationType.execTime)}
						</Typography>
					</Stack>
				</AccordionSummary>
				<AccordionDetails>
					<Grid container spacing={2} justifyContent={"space-between"}>
						<Grid item>
							<Typography>Информация об изделии</Typography>
							<Typography>Вид: {oper.product.productType.name}</Typography>
							<Typography>Статус: {oper.product.productStatus.name}</Typography>
							<Typography>Количество: {oper.product.amount}</Typography>
						</Grid>
						<Grid item>
							<ModalSetOperStatus operation={oper} operationStatuses={operationStatuses}
								page={page} loadOperations={getOperations} />
							<Typography>Формула для изделия</Typography>
							<ToothMarks teethList={oper.product.teeth} />
						</Grid>
					</Grid>
				</AccordionDetails>
			</Accordion>
		));
	}

	return (
		<Grid container sx={{
			spacing: 0,
			direction: "column",
			alignItems: "center",
			justifyContent: "center"
		}}>
			<Stack container sx={{
				display: "flex",
				width: "70%",
				minWidth: "500px",
				spacing: 3
			}}>
				<Box sx={{
					border: 1,
					borderRadius: 2,
					borderColor: '#4d4c4c',
					padding: 3,
					marginTop: 5,
					alignItems: "center"
				}}>
					<Typography textAlign={"center"} variant="h4" component="h5" sx={{ paddingBottom: 5 }}>
						Назначенные операции
					</Typography>
					{
						operations.length > 0 ?
							<>
								<Pagination count={totalPages} page={page} onChange={handleChangePage}
									variant="outlined" shape="rounded" sx={{ marginBottom: 3 }} />
								{renderOperations()}
								<Pagination count={totalPages} page={page} onChange={handleChangePage}
									variant="outlined" shape="rounded" sx={{ marginTop: 3 }} />
							</>
							:
							<Typography textAlign={"center"}>
								Нет назначенных операций
							</Typography>
					}
				</Box>
			</Stack>
		</Grid>
	);
}
export default AssignedOperations;
