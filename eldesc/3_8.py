name = '3_8'
v_coors = {'m0' : (-1,-1, -1),
          'm1' : ( 1,-1, -1),
          'm2' : ( 1, 1, -1),
          'm3' : (-1, 1, -1),
          'm4' : (-1,-1,  1),
          'm5' : ( 1,-1,  1),
          'm6' : ( 1, 1,  1),
          'm7' : (-1, 1,  1)}
v_edges = (('m0', 'm1'),
          ('m1', 'm2'),
          ('m2', 'm3'),
          ('m3', 'm0'),
          ('m4', 'm5'),
          ('m5', 'm6'),
          ('m6', 'm7'),
          ('m7', 'm4'),
          ('m0', 'm4'),
          ('m1', 'm5'),
          ('m2', 'm6'),
          ('m3', 'm7'))
v_faces = (('m0', 'm3', 'm2', 'm1'),
          ('m0', 'm4', 'm7', 'm3'),
          ('m0', 'm1', 'm5', 'm4'),
          ('m4', 'm5', 'm6', 'm7'),
          ('m1', 'm2', 'm6', 'm5'),
          ('m2', 'm3', 'm7', 'm6'))
s_coors = {'s0' : ( -1, -1),
          's1' : (  1, -1),
          's2' : (  1,  1),
          's3' : ( -1,  1)}
s_edges = {'s4' : (('s0', 's1'),
                  ('s1', 's2'),
                  ('s2', 's3'),
                  ('s3', 's0'))}
s_faces = {'s4' : ('s0', 's1', 's2', 's3')}

interpolation = '3_8_Q1'

# Not finished...
orientation = {
    'v_vecs' : (0, (1, 3, 4), (0, 1, 2, 3), (4, 5, 6, 7) ),
}
