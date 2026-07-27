# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy
import scipy
import pypardiso
import scipy.sparse
import scipy.sparse.linalg

from config.common import P4SFormat

def getPiecewiseFunctionAmplitudeFromPoint(in_point:float, in_function_params:list) -> float:
    params_number = int(len(in_function_params) * 0.5)
    defined_points_list = [i for i in in_function_params[0:params_number]]
    defined_amplitudes_list = [i for i in in_function_params[params_number:]]
    
    temp_array = numpy.zeros(params_number)
    for param_index in range(params_number):
        if param_index == 0:
            if defined_points_list[0] <= in_point < defined_points_list[1]:
                temp_array[0] = (defined_points_list[1] - in_point) / (defined_points_list[1] - defined_points_list[0])
            else:
                temp_array[0] = 0.0
        elif param_index == params_number-1:
            if defined_points_list[params_number-2] <= in_point <= defined_points_list[params_number-1]:
                temp_array[params_number-1] = (in_point - defined_points_list[params_number-2]) / (defined_points_list[params_number-1] - defined_points_list[params_number-2])
            else:
                temp_array[params_number-1] = 0.0
        else:
            if defined_points_list[param_index-1] <= in_point < defined_points_list[param_index]:
                temp_array[param_index] = (in_point - defined_points_list[param_index-1]) / (defined_points_list[param_index] - defined_points_list[param_index-1])
            elif defined_points_list[param_index] <= in_point < defined_points_list[param_index+1]:
                temp_array[param_index] = (defined_points_list[param_index+1] - in_point) / (defined_points_list[param_index+1] - defined_points_list[param_index])
            else:
                temp_array[param_index] = 0.0
    function_amplitude = numpy.sum(numpy.multiply(temp_array,defined_amplitudes_list))

    return function_amplitude



# region
def __pardiso_direct_lsolver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:    
    
    unknown_array = pypardiso.spsolve(in_coefficient_matrix.astype(numpy.dtype('float64')),in_right_array.astype(numpy.dtype('float64')))

    return unknown_array

def __scipy_cg_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, exit_code = scipy.sparse.linalg.cg(in_coefficient_matrix,in_right_array)

    if exit_code == 0:
        pass
    else:
        raise ValueError
    
    return unknown_array
def __scipy_bicgstab_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, exit_code = scipy.sparse.linalg.bicgstab(in_coefficient_matrix,in_right_array)

    if exit_code == 0:
        pass
    else:
        raise ValueError
    
    return unknown_array
def __scipy_minres_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, exit_code = scipy.sparse.linalg.minres(in_coefficient_matrix,in_right_array)

    if exit_code == 0:
        pass
    else:
        raise ValueError
    
    return unknown_array
def __scipy_gcrotmk_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, exit_code = scipy.sparse.linalg.gcrotmk(in_coefficient_matrix,in_right_array)

    if exit_code == 0:
        pass
    else:
        raise ValueError
    
    return unknown_array
def __scipy_tfqmr_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, exit_code = scipy.sparse.linalg.tfqmr(in_coefficient_matrix,in_right_array)

    if exit_code == 0:
        pass
    else:
        raise ValueError
    
    return unknown_array
def __scipy_lsmr_iterative_solver(in_coefficient_matrix:scipy.sparse.csr_matrix,in_right_array:numpy.ndarray) -> numpy.ndarray:
    unknown_array, *_ = scipy.sparse.linalg.lsmr(in_coefficient_matrix,in_right_array)
    
    return unknown_array
# endregion
lsolver_dict = {
                1:{1:__pardiso_direct_lsolver},
                2:{1:__scipy_cg_iterative_solver,2:__scipy_bicgstab_iterative_solver,
                   3:__scipy_minres_iterative_solver,4:__scipy_gcrotmk_iterative_solver,
                   5:__scipy_tfqmr_iterative_solver,6:__scipy_lsmr_iterative_solver}
                }

# region
def __adam_osolver(iter:float, alpha:float,beta:numpy.ndarray,eps:float,m:numpy.ndarray,v:numpy.ndarray,
                    df0dx:numpy.ndarray,x:numpy.ndarray, xmin:float, xmax:float, xmove:float) -> tuple:
    
    newm = beta[0] * m + (1.0 - beta[0]) * df0dx
    newv = beta[1] * v + (1.0 - beta[1]) * df0dx**2
    
    mhat = newm / (1.0 - beta[0]**float(iter))
    vaht = newv / (1.0 - beta[1]**float(iter))

    delat_x_array = - alpha * mhat / (numpy.sqrt(vaht) + eps)
    delat_x_array = numpy.minimum(xmove,numpy.maximum(-xmove,delat_x_array))

    newx = numpy.minimum(xmax,numpy.maximum(xmin,x+delat_x_array))

    return newm,newv,newx
    
def __sub_problem_solver(m:int, n:int, epsimin:float, low:numpy.ndarray, upp:numpy.ndarray, 
                        alfa: numpy.ndarray, beta: numpy.ndarray, p0:numpy.ndarray, q0:numpy.ndarray, P:numpy.ndarray, Q:numpy.ndarray, 
                        a0:float, a:numpy.ndarray, b:numpy.ndarray, c:numpy.ndarray, d:numpy.ndarray) -> tuple:

    een = numpy.ones((n, 1))
    eem = numpy.ones((m, 1))
    epsi = 1
    epsvecn = epsi * een
    epsvecm = epsi * eem
    x = 0.5 * (alfa + beta)
    y = eem.copy()
    z = numpy.array([[1.0]])
    lam = eem.copy()
    xsi = een / (x - alfa)
    xsi = numpy.maximum(xsi, een)
    eta = een / (beta - x)
    eta = numpy.maximum(eta, een)
    mu = numpy.maximum(eem, 0.5 * c)
    zet = numpy.array([[1.0]])
    s = eem.copy()
    itera = 0

    while epsi > epsimin:
        epsvecn = epsi * een
        epsvecm = epsi * eem
        ux1 = upp - x
        xl1 = x - low
        ux2 = ux1 * ux1
        xl2 = xl1 * xl1
        uxinv1 = een / ux1
        xlinv1 = een / xl1
        plam = p0 + numpy.dot(P.T, lam)
        qlam = q0 + numpy.dot(Q.T, lam)
        gvec = numpy.dot(P, uxinv1) + numpy.dot(Q, xlinv1)
        dpsidx = plam / ux2 - qlam / xl2
        rex = dpsidx - xsi + eta
        rey = c + d * y - mu - lam
        rez = a0 - zet - numpy.dot(a.T, lam)
        relam = gvec - a * z - y + s - b
        rexsi = xsi * (x - alfa) - epsvecn
        reeta = eta * (beta - x) - epsvecn
        remu = mu * y - epsvecm
        rezet = zet * z - epsi
        res = lam * s - epsvecm
        residu1 = numpy.concatenate((rex, rey, rez), axis=0)
        residu2 = numpy.concatenate((relam, rexsi, reeta, remu, rezet, res), axis=0)
        residu = numpy.concatenate((residu1, residu2), axis=0)
        residunorm = numpy.sqrt(numpy.dot(residu.T, residu).item())
        residumax = numpy.max(numpy.abs(residu))
        ittt = 0

        while (residumax > 0.9 * epsi) and (ittt < 200):
            ittt += 1
            itera += 1
            ux1 = upp - x
            xl1 = x - low
            ux2 = ux1 * ux1
            xl2 = xl1 * xl1
            ux3 = ux1 * ux2
            xl3 = xl1 * xl2
            uxinv1 = een / ux1
            xlinv1 = een / xl1
            uxinv2 = een / ux2
            xlinv2 = een / xl2
            plam = p0 + numpy.dot(P.T, lam)
            qlam = q0 + numpy.dot(Q.T, lam)
            gvec = numpy.dot(P, uxinv1) + numpy.dot(Q, xlinv1)
            GG = (scipy.sparse.diags(uxinv2.flatten(), 0).dot(P.T)).T - (scipy.sparse.diags(xlinv2.flatten(), 0).dot(Q.T)).T
            dpsidx = plam / ux2 - qlam / xl2
            delx = dpsidx - epsvecn / (x - alfa) + epsvecn / (beta - x)
            dely = c + d * y - lam - epsvecm / y
            delz = a0 - numpy.dot(a.T, lam) - epsi / z
            dellam = gvec - a * z - y - b + epsvecm / lam
            diagx = plam / ux3 + qlam / xl3
            diagx = 2 * diagx + xsi / (x - alfa) + eta / (beta - x)
            diagxinv = een / diagx
            diagy = d + mu / y
            diagyinv = eem / diagy
            diaglam = s / lam
            diaglamyi = diaglam + diagyinv

            if m < n:
                blam = dellam + dely / diagy - numpy.dot(GG, (delx / diagx))
                bb = numpy.concatenate((blam, delz), axis=0)
                Alam = numpy.asarray(scipy.sparse.diags(diaglamyi.flatten(), 0) +
                                  (scipy.sparse.diags(diagxinv.flatten(), 0).dot(GG.T).T).dot(GG.T))
                AAr1 = numpy.concatenate((Alam, a), axis=1)
                AAr2 = numpy.concatenate((a, -zet / z), axis=0).T
                AA = numpy.concatenate((AAr1, AAr2), axis=0)
                solut = scipy.linalg.solve(AA, bb)
                dlam = solut[0:m]
                dz = solut[m:m + 1]
                dx = -delx / diagx - numpy.dot(GG.T, dlam) / diagx
            else:
                diaglamyiinv = eem / diaglamyi
                dellamyi = dellam + dely / diagy
                Axx = numpy.asarray(scipy.sparse.diags(diagx.flatten(), 0) +
                                 (scipy.sparse.diags(diaglamyiinv.flatten(), 0).dot(GG).T).dot(GG))
                azz = zet / z + numpy.dot(a.T, (a / diaglamyi))
                axz = numpy.dot(-GG.T, (a / diaglamyi))
                bx = delx + numpy.dot(GG.T, (dellamyi / diaglamyi))
                bz = delz - numpy.dot(a.T, (dellamyi / diaglamyi))
                AAr1 = numpy.concatenate((Axx, axz), axis=1)
                AAr2 = numpy.concatenate((axz.T, azz), axis=1)
                AA = numpy.concatenate((AAr1, AAr2), axis=0)
                bb = numpy.concatenate((-bx, -bz), axis=0)
                solut = scipy.linalg.solve(AA, bb)
                dx = solut[0:n]
                dz = solut[n:n + 1]
                dlam = numpy.dot(GG, dx) / diaglamyi - dz * (a / diaglamyi) + dellamyi / diaglamyi

            dy = -dely / diagy + dlam / diagy
            dxsi = -xsi + epsvecn / (x - alfa) - (xsi * dx) / (x - alfa)
            deta = -eta + epsvecn / (beta - x) + (eta * dx) / (beta - x)
            dmu = -mu + epsvecm / y - (mu * dy) / y
            dzet = -zet + epsi / z - zet * dz / z
            ds = -s + epsvecm / lam - (s * dlam) / lam
            xx = numpy.concatenate((y, z, lam, xsi, eta, mu, zet, s), axis=0)
            dxx = numpy.concatenate((dy, dz, dlam, dxsi, deta, dmu, dzet, ds), axis=0)

            stepxx = -1.01 * dxx / xx
            stmxx = numpy.max(stepxx)
            stepalfa = -1.01 * dx / (x - alfa)
            stmalfa = numpy.max(stepalfa)
            stepbeta = 1.01 * dx / (beta - x)
            stmbeta = numpy.max(stepbeta)
            stmalbe = numpy.maximum(stmalfa, stmbeta)
            stmalbexx = numpy.maximum(stmalbe, stmxx)
            stminv = numpy.maximum(stmalbexx, 1.0)
            steg = 1.0 / stminv

            xold = x.copy()
            yold = y.copy()
            zold = z.copy()
            lamold = lam.copy()
            xsiold = xsi.copy()
            etaold = eta.copy()
            muold = mu.copy()
            zetold = zet.copy()
            sold = s.copy()
            
            itto = 0
            resinew = 2 * residunorm

            while (resinew > residunorm) and (itto < 50):
                itto += 1
                x = xold + steg * dx
                y = yold + steg * dy
                z = zold + steg * dz
                lam = lamold + steg * dlam
                xsi = xsiold + steg * dxsi
                eta = etaold + steg * deta
                mu = muold + steg * dmu
                zet = zetold + steg * dzet
                s = sold + steg * ds
                ux1 = upp - x
                xl1 = x - low
                ux2 = ux1 * ux1
                xl2 = xl1 * xl1
                uxinv1 = een / ux1
                xlinv1 = een / xl1
                plam = p0 + numpy.dot(P.T, lam)
                qlam = q0 + numpy.dot(Q.T, lam)
                gvec = numpy.dot(P, uxinv1) + numpy.dot(Q, xlinv1)
                dpsidx = plam / ux2 - qlam / xl2
                rex = dpsidx - xsi + eta
                rey = c + d * y - mu - lam
                rez = a0 - zet - numpy.dot(a.T, lam)
                relam = gvec - a * z - y + s - b
                rexsi = xsi * (x - alfa) - epsvecn
                reeta = eta * (beta - x) - epsvecn
                remu = mu * y - epsvecm
                rezet = zet * z - epsi
                res = lam * s - epsvecm
                residu1 = numpy.concatenate((rex, rey, rez), axis=0)
                residu2 = numpy.concatenate((relam, rexsi, reeta, remu, rezet, res), axis=0)
                residu = numpy.concatenate((residu1, residu2), axis=0)
                resinew = numpy.sqrt(numpy.dot(residu.T, residu))
                steg = steg / 2
            residunorm = resinew.copy()
            residumax = numpy.max(numpy.abs(residu))
            steg = 2 * steg

        epsi = 0.1 * epsi

    xmma = x.copy()
    ymma = y.copy()
    zmma = z.copy()
    lamma = lam
    xsimma = xsi
    etamma = eta
    mumma = mu
    zetmma = zet
    smma = s

    return xmma, ymma, zmma, lamma, xsimma, etamma, mumma, zetmma, smma
def __mma__osolver(m:int, n:int, iter:int, 
           xval:numpy.ndarray, xmin:numpy.ndarray, xmax:numpy.ndarray,
           xold1:numpy.ndarray, xold2:numpy.ndarray, 
           df0dx:numpy.ndarray, fval:numpy.ndarray, dfdx:numpy.ndarray, 
           low:numpy.ndarray, upp:numpy.ndarray,  
           move:float) -> tuple:
    
    a0 = 1.0
    a = numpy.zeros(shape=(m,1))
    c = numpy.full(shape=(m,1),fill_value=1.0e5)
    d = numpy.zeros(shape=(m,1))
    asyinit = 0.5
    asydecr = 0.7
    asyincr = 1.2, 
    asymin = 0.01
    asymax = 10
    raa0 = 0.00001 
    albefa = 0.1
    
    epsimin = 0.0000001
    eeen = numpy.ones((n, 1), dtype=P4SFormat.NUMERICAL_PRECISION['float'])
    eeem = numpy.ones((m, 1), dtype=P4SFormat.NUMERICAL_PRECISION['float'])
    zeron = numpy.zeros((n, 1), dtype=P4SFormat.NUMERICAL_PRECISION['float'])
    
    if iter <= 2:
        low = xval - asyinit * (xmax - xmin)
        upp = xval + asyinit * (xmax - xmin)
    else:
        zzz = (xval - xold1) * (xold1 - xold2)
        factor = eeen.copy()
        factor[zzz > 0] = asyincr
        factor[zzz < 0] = asydecr
        low = xval - factor * (xold1 - low)
        upp = xval + factor * (upp - xold1)
        lowmin = xval - asymax * (xmax - xmin)
        lowmax = xval - asymin * (xmax - xmin)
        uppmin = xval + asymin * (xmax - xmin)
        uppmax = xval + asymax * (xmax - xmin)
        low = numpy.maximum(low, lowmin)
        low = numpy.minimum(low, lowmax)
        upp = numpy.minimum(upp, uppmax)
        upp = numpy.maximum(upp, uppmin)

    zzz1 = low + albefa * (xval - low)
    zzz2 = xval - move * (xmax - xmin)
    zzz = numpy.maximum(zzz1, zzz2)
    alfa = numpy.maximum(zzz, xmin)
    zzz1 = upp - albefa * (upp - xval)
    zzz2 = xval + move * (xmax - xmin)
    zzz = numpy.minimum(zzz1, zzz2)
    beta = numpy.minimum(zzz, xmax)

    xmami = xmax - xmin
    xmami_eps = 0.00001 * eeen
    xmami = numpy.maximum(xmami, xmami_eps)
    xmami_inv = eeen / xmami
    ux1 = upp - xval
    ux2 = ux1 * ux1
    xl1 = xval - low
    xl2 = xl1 * xl1
    ux_inv = eeen / ux1
    xl_inv = eeen / xl1
    p0 = zeron.copy()
    q0 = zeron.copy()
    p0 = numpy.maximum(df0dx, 0)
    q0 = numpy.maximum(-df0dx, 0)
    pq0 = 0.001 * (p0 + q0) + raa0 * xmami_inv
    p0 = p0 + pq0
    q0 = q0 + pq0
    p0 = p0 * ux2
    q0 = q0 * xl2
    P = numpy.zeros((m, n), dtype=P4SFormat.NUMERICAL_PRECISION['float'])
    Q = numpy.zeros((m, n), dtype=P4SFormat.NUMERICAL_PRECISION['float'])
    P = numpy.maximum(dfdx, 0)
    Q = numpy.maximum(-dfdx, 0)
    PQ = 0.001 * (P + Q) + raa0 * numpy.dot(eeem, xmami_inv.T)
    P = P + PQ
    Q = Q + PQ
    P = (scipy.sparse.diags(ux2.flatten(), 0).dot(P.T)).T
    Q = (scipy.sparse.diags(xl2.flatten(), 0).dot(Q.T)).T
    b = numpy.dot(P, ux_inv) + numpy.dot(Q, xl_inv) - fval

    xmma, _, _, _, _, _, _, _, _ = __sub_problem_solver(
        m, n, epsimin, low, upp, alfa, beta, p0, q0, P, Q, a0, a, b, c, d)
    
    return xmma, low, upp
def __asymp_sub(outeriter:int, n:int, 
          xval:numpy.ndarray, xold1:numpy.ndarray, xold2:numpy.ndarray,
          xmin:numpy.ndarray, xmax:numpy.ndarray,
          low:numpy.ndarray, upp:numpy.ndarray,
          raa0:float, raa:numpy.ndarray,
          df0dx:numpy.ndarray, dfdx:numpy.ndarray)-> tuple:
    
    raa0eps = 0.000001
    raaeps = numpy.full(shape=raa.shape,fill_value=0.000001)
    
    asyinit = 0.5
    asydecr = 0.7
    asyincr = 1.2
    asymin = 0.01
    asymax = 10.0
    
    eeen = numpy.ones((n, 1))
    xmami = xmax - xmin
    xmamieps = 0.00001 * eeen
    xmami = numpy.maximum(xmami, xmamieps)
    raa0 = numpy.dot(numpy.abs(df0dx).T, xmami)
    raa0 = numpy.maximum(raa0eps, (0.1 / n) * raa0)
    raa = numpy.dot(numpy.abs(dfdx), xmami)
    raa = numpy.maximum(raaeps, (0.1 / n) * raa)
    
    if outeriter <= 2:
        low = xval - asyinit * xmami
        upp = xval + asyinit * xmami
    else:
        xxx = (xval - xold1) * (xold1 - xold2)
        factor = eeen.copy()
        factor[xxx > 0] = asyincr
        factor[xxx < 0] = asydecr
        low = xval - factor * (xold1 - low)
        upp = xval + factor * (upp - xold1)
        lowmin = xval - asymax * xmami
        lowmax = xval - asymin * xmami
        uppmin = xval + asymin * xmami
        uppmax = xval + asymax * xmami
        low = numpy.maximum(low, lowmin)
        low = numpy.minimum(low, lowmax)
        upp = numpy.minimum(upp, uppmax)
        upp = numpy.maximum(upp, uppmin)
    
    return low, upp, raa0, raa
def __gcmma__osolver(m:int, n:int, iter:int,
             xval:numpy.ndarray, xmin:numpy.ndarray, xmax:numpy.ndarray,
             low:numpy.ndarray, upp:numpy.ndarray,
             raa0:float, raa:numpy.ndarray, 
             f0val:numpy.ndarray, df0dx:numpy.ndarray, fval:numpy.ndarray, dfdx:numpy.ndarray,
             move:float) -> tuple: 
    
    a0 = 1.0
    a = numpy.zeros(shape=(m,1))
    c = numpy.full(shape=(m,1),fill_value=1000.0)
    d = numpy.zeros(shape=(m,1))
    epsimin = 0.0000001
    albefa = 0.1
    
    eeen = numpy.ones((n, 1))
    zeron = numpy.zeros((n, 1))

    zzz1 = low + albefa * (xval - low)
    zzz2 = xval - move * (xmax - xmin)
    zzz = numpy.maximum(zzz1, zzz2)
    alfa = numpy.maximum(zzz, xmin)
    zzz1 = upp - albefa * (upp - xval)
    zzz2 = xval + move * (xmax - xmin)
    zzz = numpy.minimum(zzz1, zzz2)
    beta = numpy.minimum(zzz, xmax)

    xmami = xmax - xmin
    xmami_eps = 0.00001 * eeen
    xmami = numpy.maximum(xmami, xmami_eps)
    xmami_inv = eeen / xmami
    ux1 = upp - xval
    ux2 = ux1 * ux1
    xl1 = xval - low
    xl2 = xl1 * xl1
    ux_inv = eeen / ux1
    xl_inv = eeen / xl1

    p0 = zeron.copy()
    q0 = zeron.copy()
    p0 = numpy.maximum(df0dx, 0)
    q0 = numpy.maximum(-df0dx, 0)
    pq0 = p0 + q0
    p0 += 0.001 * pq0
    q0 += 0.001 * pq0
    p0 += raa0 * xmami_inv
    q0 += raa0 * xmami_inv
    p0 *= ux2
    q0 *= xl2
    r0 = f0val - numpy.dot(p0.T, ux_inv) - numpy.dot(q0.T, xl_inv)
    
    P = numpy.zeros((m, n))
    Q = numpy.zeros((m, n))
    P = (scipy.sparse.diags(ux2.flatten(), 0).dot(P.T)).T
    Q = (scipy.sparse.diags(xl2.flatten(), 0).dot(Q.T)).T
    b = numpy.dot(P, ux_inv) + numpy.dot(Q, xl_inv) - fval
    P = numpy.maximum(dfdx, 0)
    Q = numpy.maximum(-dfdx, 0)
    PQ = P + Q
    P += 0.001 * PQ
    Q += 0.001 * PQ
    P += numpy.dot(raa, xmami_inv.T)
    Q += numpy.dot(raa, xmami_inv.T)
    P = (scipy.sparse.diags(ux2.flatten(), 0).dot(P.T)).T
    Q = (scipy.sparse.diags(xl2.flatten(), 0).dot(Q.T)).T
    r = fval - numpy.dot(P, ux_inv) - numpy.dot(Q, xl_inv)
    b = -r

    xmma, _, _, _, _, _, _, _, _ = __sub_problem_solver(m, n, epsimin, low, upp, alfa, beta, p0, q0, P, Q, a0, a, b, c, d)

    ux1 = upp - xmma
    xl1 = xmma - low
    ux_inv = eeen / ux1
    xl_inv = eeen / xl1
    f0app = r0 + numpy.dot(p0.T, ux_inv) + numpy.dot(q0.T, xl_inv)
    fapp = r + numpy.dot(P, ux_inv) + numpy.dot(Q, xl_inv)

    return xmma, f0app, fapp
# endregion
osolver_dict = {'ADAM':__adam_osolver, 'MMA':__mma__osolver, 'ASYMP':__asymp_sub, 'GCMMA':__gcmma__osolver}







