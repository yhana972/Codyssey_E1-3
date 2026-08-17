import json


def load_json_data(file_path: str):
    """
    Json 데이터 로드 함수
    input : file_path
    output : data
    Flow : JSON 파일 열기 -> 데이터 읽기 -> dict 반환
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        print("data.json 파일을 찾을 수 없습니다.")
        return {}  # 빈 딕셔너리를 반환하여 run_json_mode()에서 확인 그 뒤 안전하게 종료

    except json.JSONDecodeError:
        print("data.json 형식이 올바르지 않습니다.")
        return {}


def calculate_mac(pattern: list, filter_data: list) -> float:
    """
    MAC 연산 함수(패턴과 필터의 사이즈가 동일하다라는 가정하에)
    input : pattern, filter_data
    output : score
    Flow : MAC연산 ->  score 반환
    """
    score = 0.0
    size = len(pattern)

    for row in range(size):
        for col in range(size):
            score += pattern[row][col] * filter_data[row][col]

    return score


def validate_matrix(array: list) -> bool:
    """
    데이터 검증 함수 | 배열 자체가 N×N으로 정상인가?
    input : array
    output : False or True
    Flow : array의 행 갯수 계산 -> array의 행 갯수만큼 for문 ->
    각 열의 갯수와 array의 행 갯수가 같은지 비교 -> result
    """
    size = len(array)

    # array 행 갯수가 0이면 빈 배열이므로 계산 불가.
    if size == 0:
        return False

    for row in array:
        # 현재 행의 열 개수가 전체 행 개수와 다르면 N×N 배열이 아니므로 계산 불가
        if len(row) != size:
            return False

    return True


def validate_same_size(pattern: list, filter_data: list) -> bool:
    """
    데이터 검증 함수 | 두 배열의 N이 같은가?
    input : pattern, filter_data
    output : False or True
    Flow : patter과 filter_data 사이즈 비교 -> result
    """
    return len(pattern) == len(filter_data)


def input_matrix(name: str, size: int = 3) -> list:
    """
    모드 1 : 사용자 입력 (3 X 3)
    input : name, size
    output : matrix
    Flow :  사용자 입력 -> 공백 기준으로 나눔 -> 각 문자열 실수 변환 -> 완성된 한 행을 전체 배열에 넣고 -> 그 행들을 모아 2차원 배열로 return
    """
    matrix = []

    print()
    print(f"{name} 입력 (3줄 입력, 공백 구분) :")
    while (
        len(matrix) < size
    ):  # matrix에 저장된 정상 행 개수가 size보다 작은 동안 계속 반복.
        line = input()
        values = line.split()
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
            continue
    return matrix


def normalize_label(label: str) -> str:
    """
    라벨 정규화 함수
    input : label ex) +, x, cross
    output : label ex) Cross, X, Cross
    """
    if label == "+" or label == "cross":
        return "Cross"
    elif label == "x":
        return "X"
    else:
        return label


def decide_pattern(
    score_a: float, score_b: float, label_a: str = "A", label_b: str = "B"
) -> str:
    """
    점수 비교 판정 함수
    input : score_a, score_b, label_a, label_b
    output : 판정 결과
    Flow :
    두 점수 차이 확인
    -> 거의 같으면 UNDECIDED
    -> score_a가 크면 label_a
    -> score_b가 크면 label_b
    """
    # 두 점수의 차이가 1e-9보다 작으면 부동소수점 연산에서 발생할 수 있는 미세한 오차로 보고 동점으로 처리한다.
    if abs(score_a - score_b) < 1e-9:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a
    else:
        return label_b


def run_user_mode():
    """
    사용자 모드 실행 함수
    Flow : 필터 A 입력 -> 필터 B 입력 -> 패턴 입력 -> MAC(A) 계산 -> MAC(B) 계산 -> 점수 출력
    """
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("패턴")

    score_a = calculate_mac(pattern=pattern, filter_data=filter_a)
    score_b = calculate_mac(pattern=pattern, filter_data=filter_b)

    result = decide_pattern(score_a=score_a, score_b=score_b)

    print("==== MAC 결과 ====")
    print(f"A 점수 : {score_a}")
    print(f"B 점수 : {score_b}")
    print(f"판정: {result}")


def run_json_mode():
    """
    모드 2 : JSON 데이터 분석
    Flow :
    JSON 데이터 로드
    -> filters, patterns 분리
    -> 패턴 데이터 순회
    -> 패턴 크기에 맞는 필터 선택
    -> 패턴/필터 크기 검증
    """

    # 1. JSON 파일 읽기
    data = load_json_data("./data.json")

    if not data:
        print("파일을 읽지 못했습니다. data.json을 확인해주세요.")
        return

    if "filters" not in data or "patterns" not in data:
        print("data.json에 filters 또는 patterns 데이터가 없습니다.")
        return

    # 2. 필터와 패턴 데이터 분리
    filters = data["filters"]
    patterns = data["patterns"]

    pass_count = 0  # PASS가 몇 개인지 저장
    fail_count = 0  # FAIL이 몇 개인지 저장
    failures = []  # 어떤 케이스가 왜 실패 했는지 저장

    # 3. 패턴을 하나씩 순회
    for pattern_key, pattern_data in patterns.items():

        # 패턴의 실제 배열과 정답값
        pattern_input = pattern_data["input"]
        expected = normalize_label(pattern_data["expected"])

        # ex) "size_13_2" -> ["size", "13", "2"]
        parts = pattern_key.split("_")

        # 가운데 값인 13 추출
        size = parts[1]

        # ex) "size_13"
        filter_key = f"size_{size}"

        # 현재 패턴 크기에 맞는 필터 선택
        selected_filter = filters[filter_key]

        # Cross / X 필터 분리
        cross_filter = selected_filter["cross"]
        x_filter = selected_filter["x"]

        # 4. 패턴 자체가 정상적인 N x N 배열인지 검사
        if not validate_matrix(pattern_input):
            fail_count += 1
            failures.append(f"{pattern_key}: 패턴 크기 오류")
            continue

        # 5. Cross 필터가 정상적인 N x N 배열인지 검사
        if not validate_matrix(cross_filter):
            fail_count += 1
            failures.append(f"{pattern_key}: Cross 필터 크기 오류")
            continue

        # 6. X 필터가 정상적인 N x N 배열인지 검사
        if not validate_matrix(x_filter):
            fail_count += 1
            failures.append(f"{pattern_key}: X 필터 크기 오류")
            continue

        # 7. 패턴과 Cross 필터 크기가 같은지 검사
        if not validate_same_size(pattern_input, cross_filter):
            fail_count += 1
            failures.append(f"{pattern_key}: 패턴과 Cross 필터 크기 불일치")
            continue

        # 8. 패턴과 X 필터 크기가 같은지 검사
        if not validate_same_size(pattern_input, x_filter):
            fail_count += 1
            failures.append(f"{pattern_key}: 패턴과 X 필터 크기 불일치")
            continue

        cross_score = calculate_mac(pattern=pattern_input, filter_data=cross_filter)
        x_score = calculate_mac(pattern=pattern_input, filter_data=x_filter)
        decision = decide_pattern(cross_score, x_score, "Cross", "X")

        if decision == expected:
            result = "PASS"
            pass_count += 1
        else:
            result = "FAIL"
            fail_count += 1
            failures.append(f"{pattern_key}: 판정 {decision}, 정답 {expected}")

        print(f"=== {pattern_key} ===")
        print(f"Cross 점수 : {cross_score}")
        print(f"X 점수 : {x_score}")
        print(f"판정 : {decision}")
        print(f"정답 : {expected}")
        print(f"결과 : {result}")
        print()

    print("==== 전체 결과 ====")
    print(f"전체 케이스 : {len(patterns)}")
    print(f"PASS : {pass_count}")
    print(f"FAIL : {fail_count}")
    if failures:
        print("실패 케이스:")
        for failure in failures:
            print(f"- {failure}")


def main():
    while True:
        print()
        print("=== NPU 시뮬레이션 ===")
        print("1. 사용자 입력 (3X3)")
        print("2. data.json 분석")
        print("0. 종료")

        choice = input("선택 : ").strip()

        if choice == "1":
            run_user_mode()
        elif choice == "2":
            run_json_mode()
        elif choice == "0":
            print("종료")
            break
        else:
            print("올바른 값을 입력하세요.")


if __name__ == "__main__":
    main()
