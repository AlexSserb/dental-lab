import React, { useState, useEffect, useContext } from 'react';
import InfoIcon from '@mui/icons-material/Info';
import {
  Typography,
  Grid, Stack, Box,
  TextField,
  Table, TableContainer, TableHead, TableBody, TableRow, TableCell,
  Button,
  Paper,
  Pagination
} from '@mui/material';

import AuthContext from '../context/AuthContext';
import orderService from '../servicies/OrderService';
import { useNavigate } from 'react-router-dom';
import productService from '../servicies/ProductService';


const OrderList = () => {
  const { authTokens } = useContext(AuthContext);
  const [orders, setOrders] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [products, setProducts] = useState([]);
  const [currOrder, setCurrOrder] = useState({});

  const navigate = useNavigate();

  useEffect(() => {
    if (!authTokens || !authTokens.access) {
      navigate('/login');
      return;
    }

    getOrders(page);
  }, []);

  const handleChangePage = (_, newPage) => {
    setPage(newPage);
    getOrders(newPage);
  }

  const getOrders = (orderPage) => {
    orderService.getAllOrders(orderPage)
      .then(res => {
        setOrders(res.data.results);
        setTotalPages(res.data.total_pages);
        if (res.data.results.length > 0) {
          setCurrOrder(res.data.results[0]);
          getOrderInfo(res.data.results[0]);
        }
      })
      .catch(err => {
        console.log(err);
      });
  }

  const getOrderInfo = (order) => {
    productService.getForOrder(order.id)
      .then(res => {
        setProducts(res.data);
        setCurrOrder(order);
      })
      .catch(err => {
        setProducts([]);
        setCurrOrder({});
        console.log(err);
      });
  }

  // Main variable to render orders on the screen
  const renderOrders = () => {
    let i = 1;
    return orders.map((order) => (
      <TableRow key={order.id}>
        <TableCell>{i++}</TableCell>
        <TableCell sx={{ textWrap: "nowrap" }}>{order.order_date}</TableCell>
        <TableCell>{order.status.name}</TableCell>
        <TableCell sx={{ textAlign: "center" }}>
          <Button onClick={() => getOrderInfo(order)}>
            <InfoIcon />
          </Button>
        </TableCell>
      </TableRow>
    ));
  };

  const renderProducts = () => {
    let i = 1;
    return products.map(product => (
      <TableRow key={product.id}>
        <TableCell>{i++}</TableCell>
        <TableCell>{product.product_type.name}</TableCell>
        <TableCell>{product.product_status.name}</TableCell>
        <TableCell>{product.amount}</TableCell>
        <TableCell>{product.product_type.cost.toFixed(2)}</TableCell>
        <TableCell>{product.discount * 100}%</TableCell>
        <TableCell>{product.cost.toFixed(2)}</TableCell>
        <TableCell>
          <Button variant="contained" onClick={() => navigate('/operations_for_product', { state: { product: product } })}>
            <InfoIcon />
          </Button>
        </TableCell>
      </TableRow>
    ));
  }

  return (
    <Grid container spacing={3} wrap="wrap-reverse">
      <Grid item xs={4}>
        <h3 className='m-4 mt-5'>Заказы</h3>
        {
          orders.length > 0 ?
            <Stack sx={{ alignItems: "center", margin: 2 }}>
              <TableContainer component={Paper} >
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>№</TableCell>
                      <TableCell>Дата</TableCell>
                      <TableCell>Статус</TableCell>
                      <TableCell></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {renderOrders()}
                  </TableBody>
                </Table>
              </TableContainer>
              <Pagination count={totalPages} page={page} onChange={handleChangePage}
                variant="outlined" shape="rounded" sx={{ marginTop: 3 }} />
            </Stack>
            : <Typography component={Paper} sx={{
              margin: 2,
              padding: 2,
              textAlign: 'center'
            }}>
              Нет заказов
            </Typography>
        }
      </Grid>
      <Grid item xs={8}>
        <Box sx={{
          border: 1,
          borderRadius: 2,
          borderColor: '#4d4c4c',
          padding: 3,
          marginTop: 5,
        }}>
          <Typography textAlign={"center"} variant="h4" component="h4" sx={{ marginBottom: 2 }}>
            Информация о заказе
          </Typography>
          <Box>
            <Stack spacing={2}>
              {
                products.length > 0 ?
                  <TableContainer component={Paper}>
                    <Table label='Изделия'>
                      <TableHead>
                        <TableRow>
                          <TableCell>№</TableCell>
                          <TableCell>Тип изделия</TableCell>
                          <TableCell>Статус</TableCell>
                          <TableCell sx={{ width: "10%" }}>Кол-во</TableCell>
                          <TableCell>Цена</TableCell>
                          <TableCell>Скидка</TableCell>
                          <TableCell>Сумма</TableCell>
                          <TableCell>Отметки</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {renderProducts()}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  : <p for="products">Изделия для заказа</p>
              }
              <TextField
                InputProps={{ readOnly: true }}
                InputLabelProps={{ shrink: true }}
                label="Статус"
                variant="outlined"
                value={currOrder?.status?.name}
              />
              <Grid sx={{
                display: "flex",
                direction: "row",
              }}>
                {
                  currOrder?.discount !== 0 ?
                    <>
                      <TextField item
                        sx={{ width: "100%" }}
                        InputProps={{ readOnly: true }}
                        InputLabelProps={{ shrink: true }}
                        label="Сумма заказа (руб)"
                        variant="outlined"
                        value={currOrder?.cost?.toFixed(2)}
                      />
                      <TextField item
                        sx={{ width: "100%", marginX: 2 }}
                        InputProps={{ readOnly: true }}
                        InputLabelProps={{ shrink: true }}
                        label="Скидка"
                        variant="outlined"
                        value={currOrder?.discount * 100 + "%"}
                      />
                    </>
                    : <></>
                }
                <TextField item
                  sx={{ width: "100%" }}
                  InputProps={{ readOnly: true }}
                  InputLabelProps={{ shrink: true }}
                  label="Итоговая сумма заказа (руб)"
                  variant="outlined"
                  value={(currOrder?.cost * (1 - currOrder?.discount)).toFixed(2)}
                />
              </Grid>
              <TextField
                InputProps={{ readOnly: true }}
                InputLabelProps={{ shrink: true }}
                label="Дата"
                variant="outlined"
                value={currOrder?.order_date}
              />
            </Stack>
          </Box>
        </Box>
      </Grid>
    </Grid>
  )
}

export default OrderList;