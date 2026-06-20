#include <Eigen/Dense>

#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

// 如果本机已经装好 OSQP，编译时定义 USE_OSQP 就会启用这一段。
// Windows 下的 MSVC 编译命令写在 Control/README.md 中。
#ifdef USE_OSQP
extern "C" {
#include <osqp/osqp.h>
}
#endif

using Eigen::Matrix2d;
using Eigen::Matrix3d;
using Eigen::Vector2d;
using Eigen::Vector3d;

double Cost(const Vector2d& x) {
    const double dx = x(0) - 3.0;
    const double dy = x(1) - 3.0;
    return 0.5 * dx * dx + 5.0 * dy * dy;
}

Vector2d Gradient(const Vector2d& x) {
    // f = 1/2 (x-3)^2 + 10/2 (y-3)^2
    // 所以两个方向的梯度分别是 x-3 和 10(y-3)。
    return Vector2d(x(0) - 3.0, 10.0 * (x(1) - 3.0));
}

int GradientDescent(double eta, Vector2d* result) {
    Vector2d x(0.0, 0.0);
    const Vector2d target(3.0, 3.0);
    const int max_iter = 100000;

    for (int k = 0; k < max_iter; ++k) {
        if ((x - target).norm() < 1e-3) {
            *result = x;
            return k;
        }

        x = x - eta * Gradient(x);

        if (!std::isfinite(x(0)) || !std::isfinite(x(1)) || x.norm() > 1e8) {
            *result = x;
            return -1;
        }
    }

    *result = x;
    return max_iter;
}

Vector3d SolveKKTByLinearSystem() {
    // 约束 x + y <= 4 下，无约束最优点 (3,3) 不可行，所以边界会激活。
    // stationarity:
    //   x - 3 + mu = 0
    //   10(y - 3) + mu = 0
    // active constraint:
    //   x + y = 4
    Matrix3d kkt;
    kkt << 1.0, 0.0, 1.0,
           0.0, 10.0, 1.0,
           1.0, 1.0, 0.0;

    Vector3d rhs(3.0, 30.0, 4.0);
    return kkt.colPivHouseholderQr().solve(rhs);
}

void PrintQPForm() {
    Matrix2d P;
    P << 1.0, 0.0,
         0.0, 10.0;
    Vector2d q(-3.0, -30.0);
    Eigen::RowVector2d A;
    A << 1.0, 1.0;
    const double lower = -std::numeric_limits<double>::infinity();
    const double upper = 4.0;

    std::cout << "\nQ3: QP standard form\n";
    std::cout << "min 0.5 * X^T P X + q^T X,  s.t. l <= A X <= u\n";
    std::cout << "P =\n" << P << "\n";
    std::cout << "q = [" << q.transpose() << "]\n";
    std::cout << "A = [" << A << "]\n";
    std::cout << "l = " << lower << ", u = " << upper << "\n";
}

#ifdef USE_OSQP
void SolveWithOSQP() {
    const OSQPInt n = 2;
    const OSQPInt m = 1;

    // OSQP 只需要 P 的上三角部分。这里 P 是对角阵，所以只放两个非零元素。
    OSQPFloat P_x[2] = {1.0, 10.0};
    OSQPInt P_i[2] = {0, 1};
    OSQPInt P_p[3] = {0, 1, 2};

    OSQPFloat A_x[2] = {1.0, 1.0};
    OSQPInt A_i[2] = {0, 0};
    OSQPInt A_p[3] = {0, 1, 2};

    OSQPFloat q[2] = {-3.0, -30.0};
    OSQPFloat l[1] = {-OSQP_INFTY};
    OSQPFloat u[1] = {4.0};

    // vcpkg 的 Windows 动态库导出了 set_data 接口，因此这里的矩阵结构体
    // 直接放在栈上，数值数组仍由本函数管理，不需要单独释放。
    OSQPCscMatrix P{};
    OSQPCscMatrix A{};
    OSQPCscMatrix_set_data(&P, n, n, 2, P_x, P_i, P_p);
    OSQPCscMatrix_set_data(&A, m, n, 2, A_x, A_i, A_p);

    OSQPSettings settings{};
    osqp_set_default_settings(&settings);
    settings.verbose = 0;

    OSQPSolver* solver = nullptr;
    OSQPInt exitflag = osqp_setup(&solver, &P, q, &A, l, u, m, n, &settings);
    if (exitflag == 0) {
        exitflag = osqp_solve(solver);
    }

    if (exitflag == 0 && solver->info->status_val == OSQP_SOLVED) {
        std::cout << "\nOSQP solution: x = " << solver->solution->x[0]
                  << ", y = " << solver->solution->x[1]
                  << ", iteration = " << solver->info->iter << "\n";
    } else {
        std::cout << "\nOSQP did not solve the problem. exitflag = "
                  << exitflag << "\n";
    }

    if (solver != nullptr) {
        osqp_cleanup(solver);
    }
}
#endif

int main() {
    std::cout << std::fixed << std::setprecision(6);

    std::cout << "Q1: gradient descent from (0, 0)\n";
    const std::vector<double> learning_rates = {0.01, 0.05, 0.10, 0.19, 0.21};

    for (double eta : learning_rates) {
        Vector2d x;
        const int iter = GradientDescent(eta, &x);
        std::cout << "eta = " << std::setw(4) << eta << ", ";
        if (iter >= 0) {
            std::cout << "iter = " << std::setw(5) << iter
                      << ", X = [" << x.transpose() << "]"
                      << ", cost = " << Cost(x) << "\n";
        } else {
            std::cout << "not converged, last X = [" << x.transpose() << "]\n";
        }
    }

    const Vector3d kkt = SolveKKTByLinearSystem();
    std::cout << "\nQ2: KKT solution\n";
    std::cout << "x = " << kkt(0) << ", y = " << kkt(1)
              << ", mu = " << kkt(2) << "\n";
    std::cout << "check: x + y = " << kkt(0) + kkt(1)
              << ", mu >= 0 is " << (kkt(2) >= 0 ? "true" : "false") << "\n";

    PrintQPForm();

#ifdef USE_OSQP
    SolveWithOSQP();
#else
    std::cout << "\nOSQP part is written but not compiled in this run.\n";
    std::cout << "Compile with -DUSE_OSQP after installing OSQP to call the solver.\n";
#endif

    return 0;
}
