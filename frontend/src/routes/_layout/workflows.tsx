import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Skeleton,
  Table,
  Text,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiPlus } from "react-icons/fi"

import { WorkflowsService } from "@/client"

// This uses TanStack Router file-based routing
export const Route = createFileRoute("/_layout/workflows")({
  component: Workflows,
})

function WorkflowsTable() {
  const navigate = useNavigate()

  const { data: workflows, isLoading } = useQuery({
    queryFn: () => WorkflowsService.readWorkflows({}),
    queryKey: ["workflows"],
  })

  if (isLoading) {
    return (
      <Box pt={12} m={4}>
        <Skeleton height="40px" mb="4" />
        <Skeleton height="40px" mb="4" />
        <Skeleton height="40px" />
      </Box>
    )
  }

  if (!workflows?.data.length) {
    return (
      <Box p={8} textAlign="center">
        <Text fontSize="lg">No workflows found.</Text>
      </Box>
    )
  }

  return (
    <Table.Root size="sm" variant="outline">
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeader>Name</Table.ColumnHeader>
          <Table.ColumnHeader>Description</Table.ColumnHeader>
          <Table.ColumnHeader>Created</Table.ColumnHeader>
          <Table.ColumnHeader textAlign="right">Actions</Table.ColumnHeader>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {workflows.data.map((workflow) => (
          <Table.Row key={workflow.id}>
            <Table.Cell fontWeight="bold">{workflow.title}</Table.Cell>
            <Table.Cell color="gray.500">
              {workflow.description || "No description"}
            </Table.Cell>
            <Table.Cell>
              {new Date(workflow.created_at).toLocaleDateString()}
            </Table.Cell>
            <Table.Cell textAlign="right">
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate({ to: `/workflows/${workflow.id}` })}
              >
                Open Builder
              </Button>
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  )
}

function Workflows() {
  // Add workflow modal placeholder - would normally build out AddWorkflow component
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12} textAlign={{ base: "center", md: "left" }}>
        Workflows
      </Heading>

      <Flex justifyContent="space-between" alignItems="center" mt={8} mb={4}>
        <Text fontSize="md" color="ui.dim">
          Manage your workflow templates and structure.
        </Text>
        <Button variant="solid" colorPalette="teal">
          <FiPlus /> Add Workflow
        </Button>
      </Flex>
      <WorkflowsTable />
    </Container>
  )
}
