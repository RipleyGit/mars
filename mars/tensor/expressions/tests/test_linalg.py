#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 1999-2018 Alibaba Group Holding Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import numpy as np

import mars.tensor as mt
from mars.graph import DirectedGraph
from mars.tests.core import calc_shape


class Test(unittest.TestCase):
    def testQR(self):
        a = mt.random.rand(9, 6, chunk_size=(3, 6))
        q, r = mt.linalg.qr(a)

        self.assertEqual(q.shape, (9, 6))
        self.assertEqual(r.shape, (6, 6))
        self.assertEqual(calc_shape(q), ((9, 6), (6, 6)))
        self.assertEqual(calc_shape(r), ((9, 6), (6, 6)))

        q.tiles()

        self.assertEqual(len(q.chunks), 3)
        self.assertEqual(len(r.chunks), 1)
        self.assertEqual(calc_shape(q.chunks[0]), q.chunks[0].shape)
        self.assertEqual(calc_shape(r.chunks[0]), ((9, 6), (6, 6)))

        # for Short-and-Fat QR
        a = mt.random.rand(6, 18, chunk_size=(6, 6))
        q, r = mt.linalg.qr(a, method='sfqr')

        self.assertEqual(q.shape, (6, 6))
        self.assertEqual(r.shape, (6, 18))
        self.assertEqual(calc_shape(q), ((6, 6), (6, 18)))
        self.assertEqual(calc_shape(r), ((6, 6), (6, 18)))
        q.tiles()

        self.assertEqual(len(q.chunks), 1)
        self.assertEqual(len(r.chunks), 3)
        self.assertEqual(calc_shape(q.chunks[0]), ((6, 6), (6, 6)))
        self.assertEqual(calc_shape(r.chunks[0]), ((6, 6), (6, 6)))
        self.assertEqual(calc_shape(r.chunks[1]), r.chunks[1].shape)

        # chunk width less than height
        a = mt.random.rand(6, 9, chunk_size=(6, 3))
        q, r = mt.linalg.qr(a, method='sfqr')

        self.assertEqual(q.shape, (6, 6))
        self.assertEqual(r.shape, (6, 9))
        self.assertEqual(calc_shape(q), ((6, 6), (6, 9)))
        self.assertEqual(calc_shape(r), ((6, 6), (6, 9)))

        q.tiles()

        self.assertEqual(len(q.chunks), 1)
        self.assertEqual(len(r.chunks), 2)
        self.assertEqual(calc_shape(q.chunks[0]), ((6, 6), (6, 6)))
        self.assertEqual(calc_shape(r.chunks[0]), ((6, 6), (6, 6)))
        self.assertEqual(calc_shape(r.chunks[1]), r.chunks[1].shape)

        a = mt.random.rand(9, 6, chunk_size=(9, 3))
        q, r = mt.linalg.qr(a, method='sfqr')

        self.assertEqual(q.shape, (9, 6))
        self.assertEqual(r.shape, (6, 6))
        self.assertEqual(calc_shape(q), ((9, 6), (6, 6)))
        self.assertEqual(calc_shape(r), ((9, 6), (6, 6)))

        q.tiles()

        self.assertEqual(len(q.chunks), 1)
        self.assertEqual(len(r.chunks), 1)
        self.assertEqual(calc_shape(q.chunks[0]), ((9, 6), (6, 6)))
        self.assertEqual(calc_shape(r.chunks[0]), ((9, 6), (6, 6)))

    def testNorm(self):
        data = np.random.rand(9, 6)

        a = mt.tensor(data, chunk_size=(2, 6))

        for ord in (None, 'nuc', np.inf, -np.inf, 0, 1, -1, 2, -2):
            for axis in (0, 1, (0, 1)):
                for keepdims in (True, False):
                    try:
                        res = mt.linalg.norm(a, ord=ord, axis=axis, keepdims=keepdims)
                        expect_shape = np.linalg.norm(data, ord=ord, axis=axis, keepdims=keepdims).shape
                        self.assertEqual(res.shape, expect_shape)
                        self.assertEqual(calc_shape(res), expect_shape)
                    except ValueError:
                        continue

    def testSVD(self):
        a = mt.random.rand(9, 6, chunk_size=(3, 6))
        U, s, V = mt.linalg.svd(a)

        self.assertEqual(U.shape, (9, 6))
        self.assertEqual(s.shape, (6,))
        self.assertEqual(V.shape, (6, 6))
        self.assertEqual(calc_shape(U), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(s), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(V), ((9, 6), (6,), (6, 6)))

        U.tiles()
        self.assertEqual(len(U.chunks), 3)
        self.assertEqual(len(s.chunks), 1)
        self.assertEqual(len(V.chunks), 1)

        self.assertEqual(s.ndim, 1)
        self.assertEqual(len(s.chunks[0].index), 1)
        self.assertEqual(calc_shape(U.chunks[0]), U.chunks[0].shape)
        self.assertEqual(calc_shape(s.chunks[0]), ((6, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(V.chunks[0]), ((6, 6), (6,), (6, 6)))

        a = mt.random.rand(9, 6, chunk_size=(9, 6))
        U, s, V = mt.linalg.svd(a)

        self.assertEqual(U.shape, (9, 6))
        self.assertEqual(s.shape, (6,))
        self.assertEqual(V.shape, (6, 6))
        self.assertEqual(calc_shape(U), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(s), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(V), ((9, 6), (6,), (6, 6)))

        U.tiles()
        self.assertEqual(len(U.chunks), 1)
        self.assertEqual(len(s.chunks), 1)
        self.assertEqual(len(V.chunks), 1)
        self.assertEqual(calc_shape(U.chunks[0]), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(s.chunks[0]), ((9, 6), (6,), (6, 6)))
        self.assertEqual(calc_shape(V.chunks[0]), ((9, 6), (6,), (6, 6)))

        self.assertEqual(s.ndim, 1)
        self.assertEqual(len(s.chunks[0].index), 1)

        a = mt.random.rand(6, 9, chunk_size=(6, 9))
        U, s, V = mt.linalg.svd(a)

        self.assertEqual(U.shape, (6, 6))
        self.assertEqual(s.shape, (6,))
        self.assertEqual(V.shape, (6, 9))
        self.assertEqual(calc_shape(U), ((6, 6), (6,), (6, 9)))
        self.assertEqual(calc_shape(s), ((6, 6), (6,), (6, 9)))
        self.assertEqual(calc_shape(V), ((6, 6), (6,), (6, 9)))

        rs = mt.random.RandomState(1)
        a = rs.rand(9, 6, chunk_size=(3, 6))
        U, s, V = mt.linalg.svd(a)

        # test tensor graph
        graph = DirectedGraph()
        U.build_graph(tiled=False, graph=graph)
        s.build_graph(tiled=False, graph=graph)
        new_graph = DirectedGraph.from_json(graph.to_json())
        self.assertEqual((len(new_graph)), 4)
        new_outputs = [n for n in new_graph if new_graph.count_predecessors(n) == 1]
        self.assertEqual(len(new_outputs), 3)
        self.assertEqual(len(set([o.op for o in new_outputs])), 1)

        # test tensor graph, do some caculation
        graph = DirectedGraph()
        (U + 1).build_graph(tiled=False, graph=graph)
        (s + 1).build_graph(tiled=False, graph=graph)
        new_graph = DirectedGraph.from_json(graph.to_json())
        self.assertEqual((len(new_graph)), 6)
        new_outputs = [n for n in new_graph if new_graph.count_predecessors(n) == 1]
        self.assertEqual(len(new_outputs), 5)
        self.assertEqual(len(set([o.op for o in new_outputs])), 3)

        a = rs.rand(20, 10, chunk_size=10)
        _, s, _ = mt.linalg.svd(a)
        del _
        graph = s.build_graph(tiled=False)
        self.assertEqual(len(graph), 4)

    def testLU(self):
        a = mt.random.randint(1, 10, (6, 6), chunk_size=3)
        p, l, u = mt.linalg.lu(a)
        l.tiles()

        self.assertEqual(l.shape, (6, 6))
        self.assertEqual(u.shape, (6, 6))
        self.assertEqual(p.shape, (6, 6))
        self.assertEqual(calc_shape(p), p.shape)
        self.assertEqual(calc_shape(l), l.shape)
        self.assertEqual(calc_shape(u), u.shape)

        self.assertEqual(calc_shape(p.chunks[0]), p.chunks[0].shape)
        self.assertEqual(calc_shape(l.chunks[0]), l.chunks[0].shape)
        self.assertEqual(calc_shape(u.chunks[0]), u.chunks[0].shape)

    def testSolve(self):
        a = mt.random.randint(1, 10, (20, 20))
        b = mt.random.randint(1, 10, (20, ))
        x = mt.linalg.solve(a, b).tiles()

        self.assertEqual(x.shape, (20, ))
        self.assertEqual(calc_shape(x), x.shape)

        a = mt.random.randint(1, 10, (20, 20), chunk_size=5)
        b = mt.random.randint(1, 10, (20, 3), chunk_size=5)
        x = mt.linalg.solve(a, b).tiles()

        self.assertEqual(x.shape, (20, 3))
        self.assertEqual(calc_shape(x), x.shape)
        self.assertEqual(calc_shape(x.chunks[0]), x.chunks[0].shape)

    def testInv(self):
        a = mt.random.randint(1, 10, (20, 20), chunk_size=4)
        a_inv = mt.linalg.inv(a).tiles()

        self.assertEqual(a_inv.shape, (20, 20))
        self.assertEqual(calc_shape(a_inv), a_inv.shape)
        self.assertEqual(calc_shape(a_inv.chunks[0]), a_inv.chunks[0].shape)
