int main() {
	char str[20] = "input12";
	int val;
	printf("sscanf test\n");

	sscanf(str + 5, "%d", &val);

	printf("%d", strlen(str));
	printf("%s of %d\n", str, val);

	return 0;
}