import json
import time

# 프로그램에서 공통으로 사용하는 설정값
DATA_FILE_PATH = "./data.json"
USER_MATRIX_SIZE = 3
EPSILON = 1e-9
PERFORMANCE_REPEAT = 10


# JSON 모드의 3×3 성능 측정에 사용할 기본 패턴/필터
CROSS_3X3 = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
]

X_3X3 = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1],
]


def load_json_data(file_path: str) -> dict:
    """
    JSON 파일을 읽어 Python 딕셔너리로 변환하는 함수
    input : file_path
    output : JSON 전체 데이터(dict), 파일 로드 실패 시 빈 dict
    Flow : JSON 파일 열기 -> 데이터 읽기 -> dict 반환
           -> 오류 발생 시 빈 dict 반환
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("data.json 파일을 찾을 수 없습니다.")
        return {}

    except json.JSONDecodeError:
        print("data.json 형식이 올바르지 않습니다.")
        return {}


def calculate_mac(pattern: list, filter_data: list) -> float:
    """
    같은 크기의 패턴과 필터를 위치별로 곱한 뒤 모두 더하여
    MAC 점수를 계산하는 함수
    input : pattern, filter_data
    output : MAC 연산 결과 score(float)
    Flow : 행렬 크기 확인 -> 각 위치의 패턴값과 필터값 곱하기
           -> score에 누적 -> score 반환
    """
    score = 0.0
    size = len(pattern)

    for row in range(size):
        for col in range(size):
            score += pattern[row][col] * filter_data[row][col]

    return score


def flatten_matrix(matrix: list) -> list:
    """
    N×N 2차원 행렬을 N² 길이의 1차원 리스트로 변환하는 함수
    input : matrix
    output : 1차원 리스트
    Flow : 행 순회 -> 행 내부 값 순회 -> flat list에 추가
    """
    flattened = []

    for row in matrix:
        for value in row:
            flattened.append(value)

    return flattened


def calculate_mac_flat(pattern_flat: list, filter_flat: list) -> float:
    """
    1차원으로 펼친 패턴과 필터를 이용해 MAC 점수를 계산하는 함수
    input : pattern_flat, filter_flat
    output : MAC 연산 결과 score(float)
    Flow : 같은 index의 값 곱하기 -> score에 누적 -> score 반환
    """
    score = 0.0

    for index in range(len(pattern_flat)):
        score += pattern_flat[index] * filter_flat[index]

    return score


def measure_flat_performance(
    pattern_flat: list,
    filter_flat: list,
    repeat: int = PERFORMANCE_REPEAT,
) -> float:
    """
    1차원 MAC 연산을 여러 번 반복하여
    1회 평균 실행 시간을 밀리초 단위로 측정하는 함수
    input : pattern_flat, filter_flat, repeat
    output : MAC 1회당 평균 실행 시간 avg_ms(float)
    Flow : 측정 시작 -> 1차원 MAC repeat회 실행
           -> 측정 종료 -> 평균 시간 계산
    """
    start = time.perf_counter()

    for _ in range(repeat):
        calculate_mac_flat(
            pattern_flat=pattern_flat,
            filter_flat=filter_flat,
        )

    end = time.perf_counter()

    elapsed = end - start
    avg_seconds = elapsed / repeat
    avg_ms = avg_seconds * 1000

    return avg_ms


def generate_cross_pattern(size: int) -> list:
    """
    주어진 크기의 Cross 패턴을 자동 생성하는 함수
    input : size
    output : size×size Cross 패턴
    Flow : 중앙 행 또는 중앙 열이면 1, 아니면 0 저장
    """
    centers = [(size - 1) // 2, size // 2]
    pattern = []

    for row in range(size):
        line = []

        for col in range(size):
            if row in centers or col in centers:
                line.append(1)
            else:
                line.append(0)

        pattern.append(line)

    return pattern


def generate_x_pattern(size: int) -> list:
    """
    주어진 크기의 X 패턴을 자동 생성하는 함수
    input : size
    output : size×size X 패턴
    Flow : 주대각선 또는 부대각선이면 1, 아니면 0 저장
    """
    pattern = []

    for row in range(size):
        line = []

        for col in range(size):
            if row == col or row + col == size - 1:
                line.append(1)
            else:
                line.append(0)

        pattern.append(line)

    return pattern

def validate_matrix(array: list) -> bool:
    """
    입력된 2차원 배열이 비어 있지 않은 정상적인 N×N 정사각 행렬인지
    검증하는 함수
    input : array
    output : 정상적인 N×N 행렬이면 True, 아니면 False
    Flow : 행 개수 확인 -> 빈 배열 검사 -> 각 행의 열 개수 검사
           -> 검증 결과 반환
    """
    size = len(array)

    if size == 0:
        return False

    for row in array:
        if len(row) != size:
            return False

    return True


def validate_same_size(pattern: list, filter_data: list) -> bool:
    """
    패턴과 필터의 행렬 크기가 서로 같은지 검증하는 함수
    input : pattern, filter_data
    output : 두 행렬의 크기가 같으면 True, 다르면 False
    Flow : pattern의 행 개수와 filter_data의 행 개수 비교
           -> 검증 결과 반환
    """
    return len(pattern) == len(filter_data)


def validate_case_matrices(
    pattern: list,
    cross_filter: list,
    x_filter: list,
    expected_size: int,
) -> str:
    """
    JSON 테스트 케이스의 패턴과 Cross/X 필터가
    MAC 연산 가능한 크기인지 한 번에 검증하는 함수
    input : pattern, cross_filter, x_filter, expected_size
    output : 검증 성공 시 빈 문자열(""), 실패 시 실패 사유 문자열
    Flow : 각 행렬의 N×N 형태 검사
           -> 패턴과 필터 크기 비교
           -> pattern key의 N과 실제 행렬 크기 비교
           -> 검증 결과 반환
    """
    if not validate_matrix(pattern):
        return "패턴 크기 오류"

    if not validate_matrix(cross_filter):
        return "Cross 필터 크기 오류"

    if not validate_matrix(x_filter):
        return "X 필터 크기 오류"

    if not validate_same_size(pattern, cross_filter):
        return "패턴과 Cross 필터 크기 불일치"

    if not validate_same_size(pattern, x_filter):
        return "패턴과 X 필터 크기 불일치"

    if len(pattern) != expected_size:
        return (
            f"패턴 key의 크기({expected_size})와 "
            f"실제 행렬 크기({len(pattern)}) 불일치"
        )

    return ""


def input_matrix(name: str, size: int = USER_MATRIX_SIZE) -> list:
    """
    사용자로부터 공백으로 구분된 숫자를 입력받아
    N×N 행렬을 만드는 함수
    input : name, size
    output : 사용자가 정상적으로 입력한 N×N 2차원 리스트 matrix
    Flow : 행 단위 입력 -> 공백 기준 분리 -> 열 개수 검사
           -> float 변환 -> 정상 행 저장 -> N개 행 완성 후 반환
    """
    matrix = []

    print()
    print(f"{name} 입력 ({size}줄 입력, 공백 구분) :")

    while len(matrix) < size:
        values = input().split()

        if len(values) != size:
            print(
                f"입력 형식 오류: 각 줄에 {size}개의 숫자를 "
                "공백으로 구분해 입력하세요."
            )
            continue

        try:
            numbers = []

            for value in values:
                numbers.append(float(value))

            matrix.append(numbers)

        except ValueError:
            print("숫자를 입력해주세요.")

    return matrix


def normalize_label(label: str) -> str:
    """
    외부 데이터에서 사용하는 라벨을
    프로그램 내부 표준 라벨인 Cross/X로 정규화하는 함수
    input : label (+, cross, x 등)
    output : 정규화된 라벨(Cross 또는 X),
             변환 대상이 아니면 기존 label
    Flow : 라벨 변환 규칙 조회 -> 표준 라벨 반환
           -> 해당 규칙이 없으면 기존 값 반환
    """
    label_map = {
        "+": "Cross",
        "cross": "Cross",
        "Cross": "Cross",
        "x": "X",
        "X": "X",
    }

    return label_map.get(label, label)


def normalize_filters(filter_data: dict) -> dict:
    """
    JSON 필터의 key를 프로그램 내부 표준 라벨인
    Cross/X로 변환하는 함수
    input : filter_data
            예) {"cross": [...], "x": [...]}
    output : 표준 라벨을 key로 사용하는 필터 dict
             예) {"Cross": [...], "X": [...]}
    Flow : 필터 key/value 순회 -> key 정규화
           -> 새로운 dict에 저장 -> 정규화된 필터 반환
    """
    normalized_filters = {}

    for label, matrix in filter_data.items():
        normalized_label = normalize_label(label)
        normalized_filters[normalized_label] = matrix

    return normalized_filters


def extract_pattern_size(pattern_key: str):
    """
    size_N_index 형식의 패턴 key에서 행렬 크기 N을 추출하는 함수
    input : pattern_key (예: size_13_2)
    output : 추출한 행렬 크기 int,
             key 형식이 잘못된 경우 None
    Flow : "_" 기준 문자열 분리 -> key 형식 확인
           -> N을 int로 변환 -> 크기 반환
    """
    parts = pattern_key.split("_")

    if len(parts) != 3 or parts[0] != "size":
        return None

    try:
        return int(parts[1])

    except ValueError:
        return None


def decide_pattern(
    score_a: float,
    score_b: float,
    label_a: str = "A",
    label_b: str = "B",
) -> str:
    """
    두 MAC 점수를 epsilon 기준으로 비교하여
    더 높은 점수의 라벨 또는 UNDECIDED를 반환하는 함수
    input : score_a, score_b, label_a, label_b
    output : label_a, label_b 또는 UNDECIDED
    Flow : 두 점수 차이 확인
           -> epsilon보다 작으면 UNDECIDED
           -> 아니면 큰 점수에 해당하는 라벨 반환
    """
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b


def measure_performance(
    pattern: list,
    filter_data: list,
    repeat: int = PERFORMANCE_REPEAT,
) -> float:
    """
    동일한 MAC 연산을 여러 번 반복하여
    1회 평균 실행 시간을 밀리초 단위로 측정하는 함수
    input : pattern, filter_data, repeat
    output : MAC 1회당 평균 실행 시간 avg_ms(float)
    Flow : 측정 시작 -> MAC 연산 repeat회 실행 -> 측정 종료
           -> 총 시간을 반복 횟수로 나눔 -> ms 변환 후 반환
    """
    start = time.perf_counter()

    for _ in range(repeat):
        calculate_mac(
            pattern=pattern,
            filter_data=filter_data,
        )

    end = time.perf_counter()

    elapsed = end - start
    avg_seconds = elapsed / repeat
    avg_ms = avg_seconds * 1000

    return avg_ms


def analyze_performance(
    pattern: list,
    filter_data: list,
    repeat: int = PERFORMANCE_REPEAT,
):
    """
    행렬 크기별 MAC 평균 실행 시간과
    N² 연산량을 계산하는 성능 분석 함수
    input : pattern, filter_data, repeat
    output : size, avg_ms, operation_count
    Flow : 행렬 크기 확인 -> 평균 MAC 시간 측정
           -> N² 연산량 계산 -> 분석 결과 반환
    """
    size = len(pattern)

    avg_ms = measure_performance(
        pattern=pattern,
        filter_data=filter_data,
        repeat=repeat,
    )

    operation_count = size**2

    return size, avg_ms, operation_count


def add_performance_result(
    performance_results: dict,
    size: int,
    avg_ms: float,
) -> None:
    """
    특정 행렬 크기의 성능 측정값을
    크기별 성능 결과 딕셔너리에 저장하는 함수
    input : performance_results, size, avg_ms
    output : 없음(None), performance_results에 측정값 추가
    Flow : 해당 size 존재 여부 확인
           -> 없으면 빈 리스트 생성
           -> 평균 시간을 리스트에 추가
    """
    if size not in performance_results:
        performance_results[size] = []

    performance_results[size].append(avg_ms)


def measure_3x3_performance(performance_results: dict) -> None:
    """
    JSON 분석 모드의 성능 비교에 포함하기 위해
    기본 3×3 Cross/X 패턴의 MAC 성능을 측정하는 함수
    input : performance_results
    output : 없음(None), performance_results에 3×3 성능값 저장
    Flow : Cross 기준 3×3 MAC 측정
           -> X 기준 3×3 MAC 측정
           -> 두 평균 시간 계산
           -> 3×3 성능 결과 저장
    """
    _, cross_avg_ms, _ = analyze_performance(
        pattern=CROSS_3X3,
        filter_data=CROSS_3X3,
    )

    _, x_avg_ms, _ = analyze_performance(
        pattern=CROSS_3X3,
        filter_data=X_3X3,
    )

    avg_ms = (cross_avg_ms + x_avg_ms) / 2

    add_performance_result(
        performance_results=performance_results,
        size=3,
        avg_ms=avg_ms,
    )


def show_user_result(
    size: int,
    score_a: float,
    score_b: float,
    avg_a_ms: float,
    avg_b_ms: float,
    avg_ms: float,
    operation_count: int,
    decision: str,
) -> None:
    """
    사용자 입력 모드의 MAC 점수, 판정 결과,
    성능 분석 결과를 한 번에 출력하는 함수
    input : size, score_a, score_b, avg_a_ms, avg_b_ms,
            avg_ms, operation_count, decision
    output : 없음(None), 콘솔에 사용자 모드 결과 출력
    Flow : MAC 결과 출력 -> 행렬 크기와 필터별 평균 시간 출력
           -> 전체 평균 시간과 N² 연산량 출력
    """
    print()
    print("==== MAC 결과 ====")
    print(f"A 점수 : {score_a}")
    print(f"B 점수 : {score_b}")
    print(f"판정 : {decision}")

    print()
    print("==== 성능 분석 ====")
    print(f"행렬 크기 : {size}x{size}")
    print(f"A 평균 연산 시간 : {avg_a_ms:.6f} ms")
    print(f"B 평균 연산 시간 : {avg_b_ms:.6f} ms")
    print(f"평균 MAC 시간 : {avg_ms:.6f} ms")
    print(f"N² 연산량 : {operation_count}")


def build_failure_reason(
    pattern_key: str,
    decision: str,
    expected: str,
    cross_score: float,
    x_score: float,
) -> str:
    """
    JSON 테스트 실패 케이스의 원인을 요약 문장으로 만드는 함수
    input : pattern_key, decision, expected, cross_score, x_score
    output : 실패 사유 요약 문자열
    Flow : 점수 차이 계산 -> UNDECIDED 여부 확인
           -> 실패 사유 문자열 반환
    """
    score_diff = abs(cross_score - x_score)

    if decision == "UNDECIDED":
        return (
            f"{pattern_key}: 점수 차이({score_diff:.3e})가 "
            f"epsilon({EPSILON}) 범위라 UNDECIDED 판정, "
            f"정답 {expected}와 불일치"
        )

    return (
        f"{pattern_key}: Cross 점수({cross_score})와 X 점수({x_score}) 비교 결과 "
        f"{decision}로 판정되어 정답 {expected}와 불일치"
    )

def show_case_result(
    pattern_key: str,
    cross_score: float,
    x_score: float,
    cross_avg_ms: float,
    x_avg_ms: float,
    case_avg_ms: float,
    operation_count: int,
    decision: str,
    expected: str,
    result: str,
) -> None:
    """
    JSON 모드에서 테스트 케이스 1개의 MAC 점수,
    성능, 판정 및 PASS/FAIL 결과를 출력하는 함수
    input : pattern_key, cross_score, x_score,
            cross_avg_ms, x_avg_ms, case_avg_ms,
            operation_count, decision, expected, result
    output : 없음(None), 콘솔에 테스트 케이스 결과 출력
    Flow : 케이스 식별자 출력 -> Cross/X 점수와 성능 출력
           -> 판정과 정답 출력 -> PASS/FAIL 결과 출력
    """
    print(f"=== {pattern_key} ===")
    print(f"Cross 점수 : {cross_score}")
    print(f"X 점수 : {x_score}")
    print(f"Cross 평균 연산 시간 : {cross_avg_ms:.6f} ms")
    print(f"X 평균 연산 시간 : {x_avg_ms:.6f} ms")
    print(f"케이스 평균 연산 시간 : {case_avg_ms:.6f} ms")
    print(f"N² 연산량 : {operation_count}")
    print(f"판정 : {decision}")
    print(f"정답 : {expected}")
    print(f"결과 : {result}")
    print()


def show_test_summary(
    total_count: int,
    pass_count: int,
    fail_count: int,
    failures: list,
) -> None:
    """
    JSON 모드 전체 테스트의 PASS/FAIL 개수와
    실패 케이스 사유를 요약하여 출력하는 함수
    input : total_count, pass_count, fail_count, failures
    output : 없음(None), 콘솔에 전체 테스트 요약 출력
    Flow : 전체/PASS/FAIL 개수 출력
           -> 실패 목록이 있으면 케이스별 실패 사유 출력
    """
    print()
    print("==== 전체 결과 ====")
    print(f"전체 케이스 : {total_count}")
    print(f"PASS : {pass_count}")
    print(f"FAIL : {fail_count}")

    if failures:
        print("실패 케이스:")

        for failure in failures:
            print(f"- {failure}")


def show_performance_results(
    performance_results: dict,
) -> None:
    """
    수집한 성능 측정 결과를 행렬 크기순으로 정렬하여
    크기/평균 시간/N² 연산량을 하나의 표 형태로 출력하는 함수
    input : performance_results
    output : 없음(None), 콘솔에 통합 성능 분석 결과 출력
    Flow : 성능 데이터 존재 여부 확인
           -> 크기순 정렬
           -> 크기별 평균 시간 계산
           -> N² 연산량 계산
           -> 표 형태로 결과 출력
    """
    print()
    print("==== 전체 성능 분석 ====")

    if not performance_results:
        print("측정된 성능 데이터가 없습니다.")
        return

    print(f"{'크기':<10}" f"{'평균 시간(ms)':<20}" f"{'연산 횟수(N²)':<15}")
    print("-" * 45)

    for size in sorted(performance_results):
        times = performance_results[size]

        if not times:
            continue

        avg_ms = sum(times) / len(times)
        operation_count = size**2

        print(f"{size}x{size:<7}" f"{avg_ms:<20.6f}" f"{operation_count:<15}")



def input_bonus_size() -> int:
    """
    보너스 모드에서 패턴 크기 N을 입력받는 함수
    input : 콘솔 입력
    output : 1 이상의 정수 N
    Flow : 입력 받기 -> 정수 변환 -> 양수 검증 -> N 반환
    """
    while True:
        value = input("생성할 패턴 크기 N 입력 : ").strip()

        try:
            size = int(value)

        except ValueError:
            print("정수를 입력해주세요.")
            continue

        if size < 1:
            print("1 이상의 정수를 입력해주세요.")
            continue

        return size


def show_matrix(title: str, matrix: list) -> None:
    """
    2차원 행렬을 콘솔에 보기 좋게 출력하는 함수
    input : title, matrix
    output : 없음(None), 콘솔에 행렬 출력
    Flow : 제목 출력 -> 행 단위로 값 출력
    """
    print()
    print(title)

    for row in matrix:
        display_values = []

        for value in row:
            if isinstance(value, float) and value.is_integer():
                display_values.append(str(int(value)))
            else:
                display_values.append(str(value))

        print(" ".join(display_values))

def show_bonus_results(results: list) -> None:
    """
    보너스 모드의 2차원 MAC과 1차원 MAC 성능 비교 결과를 출력하는 함수
    input : results
    output : 없음(None), 콘솔에 보너스 성능 비교표 출력
    Flow : 결과 존재 여부 확인 -> 크기별 비교 결과 출력
    """
    print()
    print("==== 보너스 성능 비교 ====")

    if not results:
        print("측정된 보너스 성능 데이터가 없습니다.")
        return

    print(
        f"{'크기':<10}"
        f"{'2차원 MAC(ms)':<18}"
        f"{'1차원 MAC(ms)':<18}"
        f"{'빠른 방식':<12}"
        f"{'점수 일치':<10}"
    )
    print("-" * 70)

    for result in results:
        size = result["size"]
        normal_ms = result["normal_ms"]
        flat_ms = result["flat_ms"]
        same_score = result["same_score"]

        if abs(normal_ms - flat_ms) < EPSILON:
            faster = "동일"
        elif flat_ms < normal_ms:
            faster = "1차원"
        else:
            faster = "2차원"

        print(
            f"{size}x{size:<7}"
            f"{normal_ms:<18.6f}"
            f"{flat_ms:<18.6f}"
            f"{faster:<12}"
            f"{str(same_score):<10}"
        )

def run_user_mode() -> dict:
    """
    사용자가 입력한 3×3 필터 A/B와 패턴을 이용해
    MAC 점수와 성능을 분석하는 사용자 입력 모드 실행 함수
    input : 없음, 콘솔에서 필터 A/B와 패턴 입력
    output : 3×3 성능 측정값이 저장된 dict
    Flow : 필터 A/B 입력
           -> 필터 저장 확인
           -> 패턴 입력
           -> MAC 계산
           -> 성능 분석
           -> 판정
           -> 결과 출력
           -> 3×3 성능 결과 반환
    """
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print()
    print("필터 A/B 저장 완료")
    show_matrix("==== 저장된 필터 A ====", filter_a)
    show_matrix("==== 저장된 필터 B ====", filter_b)

    pattern = input_matrix("패턴")

    score_a = calculate_mac(
        pattern=pattern,
        filter_data=filter_a,
    )

    score_b = calculate_mac(
        pattern=pattern,
        filter_data=filter_b,
    )

    size, avg_a_ms, operation_count = analyze_performance(
        pattern=pattern,
        filter_data=filter_a,
    )

    _, avg_b_ms, _ = analyze_performance(
        pattern=pattern,
        filter_data=filter_b,
    )

    avg_ms = (avg_a_ms + avg_b_ms) / 2

    decision = decide_pattern(
        score_a=score_a,
        score_b=score_b,
    )

    show_user_result(
        size=size,
        score_a=score_a,
        score_b=score_b,
        avg_a_ms=avg_a_ms,
        avg_b_ms=avg_b_ms,
        avg_ms=avg_ms,
        operation_count=operation_count,
        decision=decision,
    )

    return {size: [avg_ms]}


def run_json_mode() -> dict:
    """
    data.json의 5×5, 13×13, 25×25 패턴과 필터를 분석하고,
    3×3을 포함한 전체 크기의 성능 결과까지 출력하는 JSON 모드 실행 함수
    input : 없음, DATA_FILE_PATH의 JSON 데이터 사용
    output : 3×3/5×5/13×13/25×25 성능 측정값이 저장된 dict
    Flow : JSON 로드
           -> filters/patterns 확인
           -> 3×3 기준 성능 측정
           -> 패턴 순회
           -> 패턴 크기 N 추출
           -> 해당 필터 선택 및 라벨 정규화
           -> 행렬 검증
           -> MAC 계산
           -> 판정 및 PASS/FAIL
           -> 크기별 성능 저장
           -> 전체 성능 분석 출력
           -> 테스트 결과 요약 출력
           -> 성능 결과 반환
    """
    data = load_json_data(DATA_FILE_PATH)

    if not data:
        return {}

    if "filters" not in data or "patterns" not in data:
        print("data.json에 filters 또는 patterns 데이터가 없습니다.")
        return {}

    filters = data["filters"]
    patterns = data["patterns"]

    pass_count = 0
    fail_count = 0
    failures = []
    performance_results = {}

    # JSON에는 5/13/25 크기만 있으므로
    # 미션 성능 비교를 위해 기본 3×3 데이터도 함께 측정한다.
    measure_3x3_performance(performance_results=performance_results)

    for pattern_key, pattern_data in patterns.items():

        # 필요한 패턴 데이터 확인
        if "input" not in pattern_data or "expected" not in pattern_data:
            fail_count += 1

            failures.append(f"{pattern_key}: input 또는 expected 데이터 없음")
            continue

        # pattern key에서 N 추출
        size = extract_pattern_size(pattern_key)

        if size is None:
            fail_count += 1

            failures.append(f"{pattern_key}: 패턴 key 형식 오류")
            continue

        # N에 맞는 필터 선택
        filter_key = f"size_{size}"

        if filter_key not in filters:
            fail_count += 1

            failures.append(f"{pattern_key}: {filter_key} 필터 없음")
            continue

        selected_filter = filters[filter_key]

        # filter key를 Cross/X 표준 라벨로 정규화
        normalized_filters = normalize_filters(selected_filter)

        if "Cross" not in normalized_filters or "X" not in normalized_filters:
            fail_count += 1

            failures.append(f"{pattern_key}: Cross 또는 X 필터 없음")
            continue

        pattern_input = pattern_data["input"]

        # expected도 동일한 표준 라벨로 정규화
        expected = normalize_label(pattern_data["expected"])

        cross_filter = normalized_filters["Cross"]
        x_filter = normalized_filters["X"]

        # 패턴과 필터 행렬 검증
        validation_error = validate_case_matrices(
            pattern=pattern_input,
            cross_filter=cross_filter,
            x_filter=x_filter,
            expected_size=size,
        )

        if validation_error:
            fail_count += 1

            failures.append(f"{pattern_key}: {validation_error}")
            continue

        # MAC 점수 계산
        cross_score = calculate_mac(
            pattern=pattern_input,
            filter_data=cross_filter,
        )

        x_score = calculate_mac(
            pattern=pattern_input,
            filter_data=x_filter,
        )

        # Cross/X 성능 분석
        _, cross_avg_ms, operation_count = analyze_performance(
            pattern=pattern_input,
            filter_data=cross_filter,
        )

        _, x_avg_ms, _ = analyze_performance(
            pattern=pattern_input,
            filter_data=x_filter,
        )

        case_avg_ms = (cross_avg_ms + x_avg_ms) / 2

        # 크기별 성능 결과 저장
        add_performance_result(
            performance_results=performance_results,
            size=size,
            avg_ms=case_avg_ms,
        )

        # Cross / X / UNDECIDED 판정
        decision = decide_pattern(
            score_a=cross_score,
            score_b=x_score,
            label_a="Cross",
            label_b="X",
        )

        # expected와 판정 비교
        if decision == expected:
            result = "PASS"
            pass_count += 1

        else:
            result = "FAIL"
            fail_count += 1

            failures.append(
                build_failure_reason(
                    pattern_key=pattern_key,
                    decision=decision,
                    expected=expected,
                    cross_score=cross_score,
                    x_score=x_score,
                )
            )

        # 케이스별 결과 출력
        show_case_result(
            pattern_key=pattern_key,
            cross_score=cross_score,
            x_score=x_score,
            cross_avg_ms=cross_avg_ms,
            x_avg_ms=x_avg_ms,
            case_avg_ms=case_avg_ms,
            operation_count=operation_count,
            decision=decision,
            expected=expected,
            result=result,
        )

    # 미션 요구 순서:
    # MAC/PASS-FAIL -> 성능 분석 -> 결과 요약
    show_performance_results(performance_results=performance_results)

    show_test_summary(
        total_count=len(patterns),
        pass_count=pass_count,
        fail_count=fail_count,
        failures=failures,
    )

    return performance_results


def run_bonus_mode() -> None:
    """
    보너스 모드 실행 함수
    input : 콘솔에서 패턴 크기 N 입력
    output : 없음(None), 자동 생성 패턴과 2차원/1차원 MAC 성능 비교 출력
    Flow : N 입력
           -> N×N Cross/X 패턴 자동 생성
           -> 생성 패턴 출력
           -> 2차원 MAC 측정
           -> 1차원 변환 후 MAC 측정
           -> 점수 일치 여부 확인
           -> 비교 결과 출력
    """
    size = input_bonus_size()

    pattern = generate_cross_pattern(size)
    filter_data = generate_x_pattern(size)

    show_matrix(f"==== {size}x{size} Cross 패턴 ====", pattern)
    show_matrix(f"==== {size}x{size} X 패턴 ====", filter_data)

    if not validate_matrix(pattern) or not validate_matrix(filter_data):
        print("자동 생성된 패턴이 N×N 형식이 아닙니다.")
        return

    if not validate_same_size(pattern, filter_data):
        print("자동 생성된 Cross/X 패턴 크기가 서로 다릅니다.")
        return

    normal_score = calculate_mac(
        pattern=pattern,
        filter_data=filter_data,
    )

    _, normal_ms, _ = analyze_performance(
        pattern=pattern,
        filter_data=filter_data,
    )

    pattern_flat = flatten_matrix(pattern)
    filter_flat = flatten_matrix(filter_data)

    flat_score = calculate_mac_flat(
        pattern_flat=pattern_flat,
        filter_flat=filter_flat,
    )

    flat_ms = measure_flat_performance(
        pattern_flat=pattern_flat,
        filter_flat=filter_flat,
    )

    same_score = abs(normal_score - flat_score) < EPSILON

    print()
    print("==== 보너스 MAC 점수 비교 ====")
    print(f"2차원 MAC 점수 : {normal_score}")
    print(f"1차원 MAC 점수 : {flat_score}")
    print(f"점수 일치 : {same_score}")

    show_bonus_results(
        [
            {
                "size": size,
                "normal_ms": normal_ms,
                "flat_ms": flat_ms,
                "same_score": same_score,
            }
        ]
    )

def main() -> None:
    """
    NPU 시뮬레이터의 메인 메뉴를 관리하고
    사용자가 선택한 실행 모드를 호출하는 함수
    input : 없음, 콘솔에서 메뉴 번호 입력
    output : 없음(None)
    Flow : 메뉴 출력
           -> 사용자 선택
           -> 사용자 입력 또는 JSON 분석 실행
           -> 필요 시 마지막 성능 결과 다시 출력
           -> 종료 전까지 반복
    """
    performance_results = {}

    while True:
        print()
        print("=== Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("3. 마지막 성능 분석 다시 보기")
        print("4. 보너스 성능 비교")
        print("0. 종료")

        choice = input("선택 : ").strip()

        if choice == "1":
            performance_results = run_user_mode()

        elif choice == "2":
            performance_results = run_json_mode()

        elif choice == "3":
            show_performance_results(performance_results)

        elif choice == "4":
            run_bonus_mode()

        elif choice == "0":
            print("종료")
            break

        else:
            print("올바른 값을 입력하세요.")


if __name__ == "__main__":
    main()
