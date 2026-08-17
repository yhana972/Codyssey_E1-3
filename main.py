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

            failures.append(f"{pattern_key}: " f"판정 {decision}, 정답 {expected}")

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
        print("0. 종료")

        choice = input("선택 : ").strip()

        if choice == "1":
            performance_results = run_user_mode()

        elif choice == "2":
            performance_results = run_json_mode()

        elif choice == "3":
            show_performance_results(performance_results)

        elif choice == "0":
            print("종료")
            break

        else:
            print("올바른 값을 입력하세요.")


if __name__ == "__main__":
    main()
