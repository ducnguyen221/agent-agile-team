# Ví dụ cài đặt endpoint (TypeScript, Python, Go)

> **Kết luận:** cùng một endpoint "tạo người dùng" ở ba ngăn xếp, cùng bốn bước: kiểm đầu vào bằng
> schema → trả 422 kèm lỗi từng trường → tạo → trả 201 kèm `Location`. Lỗi miền đã biết ánh xạ sang mã
> riêng (409); lỗi lạ trả 500 với thông điệp chung, chi tiết chỉ vào log.

## 1. TypeScript (Next.js API Route)

```typescript
import { z } from "zod";
import { NextRequest, NextResponse } from "next/server";

const createCustomerSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = createCustomerSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({
      error: {
        code: "validation_error",
        message: "Request validation failed",
        details: parsed.error.issues.map(i => ({
          field: i.path.join("."),
          message: i.message,
          code: i.code,
        })),
      },
    }, { status: 422 });
  }

  const customer = await createCustomer(parsed.data);

  return NextResponse.json(
    { data: customer },
    { status: 201, headers: { Location: `/api/v1/customers/${customer.id}` } },
  );
}
```

## 2. Python (Django REST Framework)

```python
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

class CreateCustomerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "email", "name", "created_at"]

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateCustomerSerializer
        return CustomerSerializer

    def create(self, request):
        serializer = CreateCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = CustomerService.create(**serializer.validated_data)
        return Response(
            {"data": CustomerSerializer(customer).data},
            status=status.HTTP_201_CREATED,
            headers={"Location": f"/api/v1/customers/{customer.id}"},
        )
```

Cài bằng FastAPI: xem skill `fastapi`.

## 3. Go (net/http)

```go
func (h *CustomerHandler) CreateCustomer(w http.ResponseWriter, r *http.Request) {
    var req CreateCustomerRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid_json", "Invalid request body")
        return
    }

    if err := req.Validate(); err != nil {
        writeError(w, http.StatusUnprocessableEntity, "validation_error", err.Error())
        return
    }

    customer, err := h.service.Create(r.Context(), req)
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrEmailTaken):
            writeError(w, http.StatusConflict, "email_taken", "Email already registered")
        default:
            writeError(w, http.StatusInternalServerError, "internal_error", "Internal error")
        }
        return
    }

    w.Header().Set("Location", fmt.Sprintf("/api/v1/customers/%s", customer.ID))
    writeJSON(w, http.StatusCreated, map[string]any{"data": customer})
}
```
